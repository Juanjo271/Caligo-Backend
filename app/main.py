from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .database import init_db
from .routers import pois, vision, rutas, audio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI(
    title="CaliGuía API",
    description="Backend para CaliGuía Go - Asistente Turístico Inteligente de Cali",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pois.router)
app.include_router(vision.router)
app.include_router(rutas.router)
app.include_router(audio.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup_event():
    init_db()
    print("=" * 50)
    print("CaliGuía API iniciada correctamente")
    print("Documentación: http://localhost:8000/docs")
    print("=" * 50)


@app.get("/")
def root():
    return {
        "mensaje": "¡Oís! Bienvenido a CaliGuía API",
        "version": "1.0.0",
        "documentacion": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
