from fastapi import APIRouter, HTTPException
from typing import List
import sqlite3
import json

from app.models import POIBase, POIListItem
from app.database import DB_PATH

router = APIRouter(prefix="/api/pois", tags=["POIs"])


def row_to_poi(row: sqlite3.Row) -> POIBase:
    tags = json.loads(row["tags"]) if row["tags"] else []
    return POIBase(
        id=row["id"],
        nombre=row["nombre"],
        categoria=row["categoria"],
        tags=tags,
        lat=row["lat"],
        lon=row["lon"],
        radio_metros=row["radio_metros"],
        descripcion=row["descripcion"],
        historia=row["historia"],
        imagen_referencia=row["imagen_referencia"],
        audio_narracion=row["audio_narracion"],
        es_legendario=bool(row["es_legendario"]),
    )


def row_to_poi_list_item(row: sqlite3.Row) -> POIListItem:
    tags = json.loads(row["tags"]) if row["tags"] else []
    return POIListItem(
        id=row["id"],
        nombre=row["nombre"],
        categoria=row["categoria"],
        tags=tags,
        lat=row["lat"],
        lon=row["lon"],
        radio_metros=row["radio_metros"],
        es_legendario=bool(row["es_legendario"]),
    )


@router.get("", response_model=List[POIListItem])
def get_pois():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, categoria, tags, lat, lon, radio_metros,
               descripcion, historia, imagen_referencia, audio_narracion, es_legendario
        FROM pois
    """)
    rows = cursor.fetchall()
    conn.close()
    return [row_to_poi_list_item(row) for row in rows]


@router.get("/{poi_id}", response_model=POIBase)
def get_poi(poi_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, categoria, tags, lat, lon, radio_metros,
               descripcion, historia, imagen_referencia, audio_narracion, es_legendario
        FROM pois WHERE id = ?
    """, (poi_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="POI no encontrado")
    return row_to_poi(row)


@router.get("/{poi_id}/image")
def get_poi_image(poi_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT imagen_referencia FROM pois WHERE id = ?", (poi_id,))
    row = cursor.fetchone()
    conn.close()
    if not row or not row["imagen_referencia"]:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return {"image_filename": row["imagen_referencia"]}
