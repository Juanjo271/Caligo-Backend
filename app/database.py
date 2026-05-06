import sqlite3
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "caliguia.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

SEED_POIS_PATH = os.path.join(BASE_DIR, "app", "core", "config", "seed_pois.json")


def load_seed_pois():
    if os.path.exists(SEED_POIS_PATH):
        with open(SEED_POIS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


POIS_DATA = load_seed_pois()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pois (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT,
            tags TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            radio_metros INTEGER DEFAULT 50,
            descripcion TEXT,
            historia TEXT,
            imagen_referencia TEXT,
            audio_narracion TEXT,
            es_legendario INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orb_descriptors (
            poi_id INTEGER PRIMARY KEY,
            descriptor BLOB,
            image_path TEXT,
            FOREIGN KEY (poi_id) REFERENCES pois(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poi_id INTEGER,
            timestamp INTEGER,
            attempts INTEGER DEFAULT 0,
            bypassed INTEGER DEFAULT 0,
            FOREIGN KEY (poi_id) REFERENCES pois(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 1,
            created_at INTEGER
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM pois")
    if cursor.fetchone()[0] == 0:
        for poi in POIS_DATA:
            tags_json = json.dumps(poi.get("tags", []))
            cursor.execute("""
                INSERT INTO pois (id, nombre, categoria, tags, lat, lon, radio_metros,
                                  descripcion, historia, imagen_referencia, audio_narracion, es_legendario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                poi["id"], poi["nombre"], poi["categoria"], tags_json,
                poi["lat"], poi["lon"], poi.get("radio_metros", 50),
                poi.get("descripcion"), poi.get("historia"),
                poi.get("imagen_referencia"), poi.get("audio_narracion"), poi.get("es_legendario", 0)
            ))
        print(f"Se insertaron {len(POIS_DATA)} POIs en la base de datos.")

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash("admin123")
        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO users (username, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?)
        """, ("admin", password_hash, 1, timestamp))
        print("Usuario admin creado: username='admin', password='admin123'")

    conn.commit()
    conn.close()
    print(f"Base de datos inicializada en: {DB_PATH}")


if __name__ == "__main__":
    init_db()
