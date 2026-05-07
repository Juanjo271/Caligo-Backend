import pytest
import sqlite3
import os
import sys
import tempfile
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a test database
TEST_DB = tempfile.mktemp(suffix=".db")


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment."""
    os.environ["CALIGUIA_DATABASE_PATH"] = TEST_DB
    yield
    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    # Create test database
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE pois (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 1,
            created_at INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poi_id INTEGER,
            timestamp INTEGER,
            attempts INTEGER DEFAULT 0,
            bypassed INTEGER DEFAULT 0,
            FOREIGN KEY (poi_id) REFERENCES pois(id)
        )
    """)

    # Insert test data
    cursor.execute("""
        INSERT INTO pois (nombre, categoria, tags, lat, lon, radio_metros, descripcion, historia, es_legendario)
        VALUES ('Iglesia La Ermita', 'Arquitectura', '["historia", "religioso"]', 3.4516, -76.5321, 50, 'Iglesia colonial del siglo XVIII', 'La Ermita fue construida en 1780...', 0)
    """)

    cursor.execute("""
        INSERT INTO pois (nombre, categoria, tags, lat, lon, radio_metros, descripcion, historia, es_legendario)
        VALUES ('Catedral de San Pedro', 'Religioso', '["iglesia", "colonial"]', 3.4520, -76.5310, 50, 'La catedral principal de Cali', 'Construida en 1908...', 1)
    """)

    conn.commit()
    conn.close()

    yield TEST_DB

    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database."""
    # Import app module
    import app.main as main_module
    import app.database as db_module

    # Save original DB path
    original_db = db_module.DB_PATH

    # Override to test database
    db_module.DB_PATH = TEST_DB

    # Create client with the app
    with TestClient(main_module.app) as test_client:
        yield test_client

    # Restore original
    db_module.DB_PATH = original_db
