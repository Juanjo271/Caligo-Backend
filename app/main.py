from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os

from app.core.settings import settings
from app.core.limiter import limiter
from app.database import init_db
from app.routers import pois, vision, rutas, audio, admin, admin_pages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, settings.static_dir)
TEMPLATE_DIR = os.path.join(BASE_DIR, "app", "templates")
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - restrict to known origins in production
cors_origins = settings.cors_origins if settings.cors_origins != ["*"] else [
    "http://localhost",
    "http://localhost:8080",
    "http://10.42.0.1:8000",
    "http://10.42.0.1:8080",
    "caliguia://",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(pois.router)
app.include_router(vision.router)
app.include_router(rutas.router)
app.include_router(audio.router)
app.include_router(admin.router)
app.include_router(admin_pages.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup_event():
    init_db()
    banner_width = 50
    print("=" * banner_width)
    print(f"{settings.app_title} iniciada correctamente")
    print(f"Documentación: http://localhost:8000/docs")
    print("=" * banner_width)


@app.get("/")
def root():
    return {
        "mensaje": "¡Oís! Bienvenido a CaliGuía API",
        "version": settings.app_version,
        "documentacion": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
