from fastapi import APIRouter, Query
from typing import List, Optional
import sqlite3
import json
import math
from datetime import datetime

from ..models import POIListItem, RutaResponse, ConfigResponse
from ..database import DB_PATH

router = APIRouter(prefix="/api", tags=["Rutas y Config"])


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def calculate_score(poi_tags: List[str], perfil: str, distance: float) -> float:
    tag_scores = {
        "salsa": ["Salsa", "Música", "Cultura", "Nocturna"],
        "naturaleza": ["Naturaleza", "Río", "Ecoturismo", "Biodiversidad"],
        "historia": ["Historia", "Patrimonio", "Arquitectura", "Religioso"],
        "gastronomia": ["Gastronomía", "Comida", "Mercado"],
        "medico": ["Salud", "Bienestar", "Médico"],
    }

    relevant_tags = tag_scores.get(perfil.lower(), [])
    tag_match = sum(1 for tag in poi_tags if tag in relevant_tags) / max(len(relevant_tags), 1)

    distance_score = max(0, 1 - (distance / 5000))

    return 0.6 * tag_match + 0.4 * distance_score


@router.get("/ruta", response_model=RutaResponse)
def get_ruta(
    perfil: str = Query(..., description="salsa, naturaleza, historia, gastronomia"),
    lat: float = Query(...),
    lon: float = Query(...),
    cantidad: int = Query(default=4, ge=1, le=10),
):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, categoria, tags, lat, lon, radio_metros, es_legendario
        FROM pois
    """)
    rows = cursor.fetchall()
    conn.close()

    scored_pois = []
    for row in rows:
        tags = json.loads(row["tags"]) if row["tags"] else []
        distance = haversine_distance(lat, lon, row["lat"], row["lon"])
        score = calculate_score(tags, perfil, distance)
        scored_pois.append({
            "row": row,
            "distance": distance,
            "score": score,
        })

    scored_pois.sort(key=lambda x: (-x["score"], x["distance"]))

    selected = scored_pois[:cantidad]

    pois = []
    for item in selected:
        row = item["row"]
        tags = json.loads(row["tags"]) if row["tags"] else []
        pois.append(POIListItem(
            id=row["id"],
            nombre=row["nombre"],
            categoria=row["categoria"],
            tags=tags,
            lat=row["lat"],
            lon=row["lon"],
            radio_metros=row["radio_metros"],
            es_legendario=bool(row["es_legendario"]),
        ))

    ruta_personalizada = [p.id for p in pois]

    return RutaResponse(pois=pois, ruta_personalizada=ruta_personalizada)


@router.get("/config/evento", response_model=ConfigResponse)
def get_evento_config():
    hoy = datetime.now()
    mes = hoy.month

    if mes == 12:
        return ConfigResponse(
            modo_evento="feria",
            evento_activo=True,
            informacion="¡Feria de Cali! Eventos por toda la ciudad. La Salsa está爆."
        )
    elif mes == 8:
        return ConfigResponse(
            modo_evento="petronio",
            evento_activo=True,
            informacion="¡Festival Petronio Álvarez! La música del Pacífico está en su hogar."
        )
    elif mes == 3 or mes == 4:
        return ConfigResponse(
            modo_evento="semana_santa",
            evento_activo=True,
            informacion="Semana Santa en Cali. Procesiones y tradiciones religiosas."
        )
    elif mes == 6:
        return ConfigResponse(
            modo_evento="birdfair",
            evento_activo=True,
            informacion="Colombia BirdFair - Avistamiento de aves. 562 especies te esperan."
        )
    else:
        return ConfigResponse(
            modo_evento="normal",
            evento_activo=False,
            informacion="Sin eventos especiales activos."
        )


@router.post("/checkin")
def register_checkin(poi_id: int, bypassed: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pois WHERE id = ?", (poi_id,))
    if not cursor.fetchone():
        conn.close()
        return {"success": False, "mensaje": "POI no encontrado"}

    timestamp = int(datetime.now().timestamp())

    cursor.execute("""
        INSERT INTO checkins (poi_id, timestamp, bypassed)
        VALUES (?, ?, ?)
    """, (poi_id, timestamp, 1 if bypassed else 0))

    conn.commit()
    conn.close()

    return {"success": True, "mensaje": "Check-in registrado"}
