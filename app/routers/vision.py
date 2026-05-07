from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
import sqlite3
import json
import os

from ..models import VerifyResponse
from ..database import DB_PATH
from ..services.matcher import get_orb_matcher
from ..core.limiter import limiter
from ..core.settings import settings

router = APIRouter(prefix="/api/vision", tags=["Visión"])


@router.post("/match/{poi_id}", response_model=VerifyResponse)
@limiter.limit(settings.rate_limit_admin_write)
async def match_image(request: Request, poi_id: int, file: UploadFile = File(...)):
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

    poi_nombre = row["nombre"]
    expected_filename = row["imagen_referencia"]

    contents = await file.read()

    matcher = get_orb_matcher()
    match, score = matcher.verify(contents, expected_filename)

    if match:
        mensaje = f"¡Encontrado! Este es {poi_nombre}. ¡Descubriste un nuevo lugar!"
    else:
        mensaje = f"Eso no parece {poi_nombre}. Intentá de nuevo, parce."

    return VerifyResponse(
        match=match,
        score=round(score, 2),
        poi_id=poi_id,
        poi_nombre=poi_nombre,
        mensaje=mensaje,
    )
