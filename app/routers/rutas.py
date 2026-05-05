from fastapi import APIRouter, Query
from typing import List
import sqlite3
import json
import math
from datetime import datetime
import os

from app.models import POIListItem, RutaResponse, ConfigResponse
from app.database import DB_PATH
from app.core.settings import settings

router = APIRouter(prefix="/api", tags=["Rutas y Config"])

EARTH_RADIUS_METERS = 6371000

PROFILES = {}
PROFILES_LOADED = False


def load_profiles():
    global PROFILES, PROFILES_LOADED
    if not PROFILES_LOADED:
        profiles_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            settings.profiles_file
        )
        if os.path.exists(profiles_path):
            with open(profiles_path, "r", encoding="utf-8") as f:
                PROFILES = json.load(f)
        PROFILES_LOADED = True


EVENTS_CONFIG = {}
EVENTS_LOADED = False


def load_events():
    global EVENTS_CONFIG, EVENTS_LOADED
    if not EVENTS_LOADED:
        events_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            settings.events_file
        )
        if os.path.exists(events_path):
            with open(events_path, "r", encoding="utf-8") as f:
                EVENTS_CONFIG = json.load(f)
        EVENTS_LOADED = True


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_METERS * c


def calculate_score(poi_tags: List[str], perfil: str, distance: float) -> float:
    load_profiles()
    tag_scores = PROFILES.get(perfil.lower(), {}).get("tags", [])

    tag_match = sum(1 for tag in poi_tags if tag in tag_scores) / max(len(tag_scores), 1)

    distance_score = max(0, 1 - (distance / settings.max_scoring_distance))

    return settings.tag_match_weight * tag_match + settings.distance_score_weight * distance_score


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
    load_events()
    hoy = datetime.now()
    mes = hoy.month

    events = EVENTS_CONFIG.get("events", [])
    for event in events:
        months = event.get("months", [event.get("month")])
        if mes in months:
            return ConfigResponse(
                modo_evento=event["mode"],
                evento_activo=True,
                informacion=event["information"]
            )

    default = EVENTS_CONFIG.get("default", {
        "mode": "normal",
        "evento_activo": False,
        "information": "Sin eventos especiales activos."
    })
    return ConfigResponse(
        modo_evento=default["mode"],
        evento_activo=default.get("evento_activo", False),
        informacion=default["information"]
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
