import sqlite3
import json
from typing import List, Optional
from app.database import DB_PATH
from app.models import POICreate, POIUpdate
from app.services.tts_service import generate_audio_sync


def create_poi(poi_data: POICreate) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pois (nombre, categoria, tags, lat, lon, radio_metros,
                          descripcion, historia, imagen_referencia, audio_narracion, es_legendario)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        poi_data.nombre,
        poi_data.categoria,
        poi_data.tags,
        poi_data.lat,
        poi_data.lon,
        poi_data.radio_metros,
        poi_data.descripcion,
        poi_data.historia,
        "",  # imagen_referencia
        "",  # audio_narracion
        1 if poi_data.es_legendario else 0,
    ))

    poi_id = cursor.lastrowid
    conn.commit()
    conn.close()

    if poi_data.generate_audio and poi_data.historia:
        audio_filename = generate_audio_sync(poi_data.historia, poi_id)
        if audio_filename:
            update_poi_audio(poi_id, audio_filename)

    return poi_id


def update_poi(poi_id: int, poi_data: POIUpdate) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pois WHERE id = ?", (poi_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return False

    fields = []
    values = []

    if poi_data.nombre is not None:
        fields.append("nombre = ?")
        values.append(poi_data.nombre)
    if poi_data.categoria is not None:
        fields.append("categoria = ?")
        values.append(poi_data.categoria)
    if poi_data.tags is not None:
        fields.append("tags = ?")
        values.append(poi_data.tags)
    if poi_data.lat is not None:
        fields.append("lat = ?")
        values.append(poi_data.lat)
    if poi_data.lon is not None:
        fields.append("lon = ?")
        values.append(poi_data.lon)
    if poi_data.radio_metros is not None:
        fields.append("radio_metros = ?")
        values.append(poi_data.radio_metros)
    if poi_data.descripcion is not None:
        fields.append("descripcion = ?")
        values.append(poi_data.descripcion)
    if poi_data.historia is not None:
        fields.append("historia = ?")
        values.append(poi_data.historia)
    if poi_data.es_legendario is not None:
        fields.append("es_legendario = ?")
        values.append(1 if poi_data.es_legendario else 0)
    if poi_data.imagen_referencia is not None:
        fields.append("imagen_referencia = ?")
        values.append(poi_data.imagen_referencia)
    if poi_data.audio_narracion is not None:
        fields.append("audio_narracion = ?")
        values.append(poi_data.audio_narracion)

    if not fields:
        conn.close()
        return True

    values.append(poi_id)
    query = f"UPDATE pois SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True


def update_poi_audio(poi_id: int, audio_filename: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE pois SET audio_narracion = ? WHERE id = ?", (audio_filename, poi_id))
    conn.commit()
    conn.close()


def update_poi_image(poi_id: int, image_filename: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE pois SET imagen_referencia = ? WHERE id = ?", (image_filename, poi_id))
    conn.commit()
    conn.close()


def delete_poi(poi_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pois WHERE id = ?", (poi_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_poi(poi_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pois WHERE id = ?", (poi_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_pois(search: str = "", category: str = "", tag: str = "", limit: int = 50, offset: int = 0) -> List[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM pois WHERE 1=1"
    params = []

    if search:
        query += " AND (nombre LIKE ? OR descripcion LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        query += " AND categoria LIKE ?"
        params.append(f"%{category}%")

    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def count_pois(search: str = "", category: str = "", tag: str = "") -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM pois WHERE 1=1"
    params = []

    if search:
        query += " AND (nombre LIKE ? OR descripcion LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        query += " AND categoria LIKE ?"
        params.append(f"%{category}%")

    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM pois")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pois WHERE es_legendario = 1")
    legendary = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT poi_id) FROM checkins")
    discovered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM checkins WHERE bypassed = 1")
    bypassed = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM pois ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    recent = [dict(zip(cols, row)) for row in rows]

    conn.close()

    return {
        "total_pois": total,
        "legendary_pois": legendary,
        "discovered_count": discovered,
        "bypassed_count": bypassed,
        "recent_pois": recent,
    }


def get_categories() -> List[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT categoria FROM pois ORDER BY categoria")
    categories = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return categories


def get_all_tags() -> List[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT tags FROM pois")
    all_tags = set()
    for row in cursor.fetchall():
        if row[0]:
            try:
                tags = json.loads(row[0])
                all_tags.update(tags)
            except json.JSONDecodeError:
                continue
    conn.close()
    return sorted(list(all_tags))
