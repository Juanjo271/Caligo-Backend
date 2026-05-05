from fastapi import APIRouter, HTTPException
from typing import List
import sqlite3
import json

from ..models import POIBase, POIListItem
from ..database import DB_PATH

router = APIRouter(prefix="/api/pois", tags=["POIs"])


def row_to_poi(row) -> POIBase:
    tags = json.loads(row[3]) if row[3] else []
    return POIBase(
        id=row[0],
        nombre=row[1],
        categoria=row[2],
        tags=tags,
        lat=row[4],
        lon=row[5],
        radio_metros=row[6],
        descripcion=row[7],
        historia=row[8],
        imagen_referencia=row[9],
        audio_narracion=row[10],
        es_legendario=bool(row[11]),
    )


def row_to_poi_list_item(row) -> POIListItem:
    tags = json.loads(row[3]) if row[3] else []
    return POIListItem(
        id=row[0],
        nombre=row[1],
        categoria=row[2],
        tags=tags,
        lat=row[4],
        lon=row[5],
        radio_metros=row[6],
        es_legendario=bool(row[11]),
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
    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return {"image_filename": row[0]}
