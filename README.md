# CaliGuía Go - Backend

FastAPI backend para CaliGuía Go - Asistente Turístico Inteligente de Cali, Colombia.

## Características

- **API REST** con FastAPI
- **POIs** - Gestión de puntos de interés turísitico
- **Visión** - Verificación de fotos con OpenCV
- **TTS** - Narración con texto a voz
- **Rutas** - Generación de rutas turísticas personalizadas
- **Check-in** - Sistema de descubrimiento de lugares

## Tech Stack

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **OpenCV** - Visión por computadora
- **gTTS** - Google Text-to-Speech
- **SQLite** - Base de datos (desarrollo)

## Requisitos

- Python 3.11+
- OpenCV
- espeak-ng o gTTS para TTS

## Instalación

### 1. Clonar

```bash
git clone https://github.com/Juanjo271/Caligo-Backend.git
cd Caligo-Backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Variables de entorno (opcional)

```bash
export CALIGUIA_BACKEND_URL=http://localhost:8000
```

### 5. Ejecutar

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Verificar

```bash
curl http://localhost:8000/health
```

## Endpoints

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/pois` | Lista de POIs |
| GET | `/api/pois/{id}` | Detalle de POI |
| GET | `/api/ruta` | Ruta turística |
| POST | `/api/vision/match/{id}` | Verificar foto |
| GET | `/api/config/evento` | Config del evento |
| POST | `/api/checkin` | Registrar check-in |
| GET | `/api/audio/{id}.mp3` | Audio TTS |
| GET | `/static/ref_images/{file}` | Imágenes de referencia |

## Estructura

```
backend/
├── app/
│   ├── main.py           # Entry point FastAPI
│   ├── models.py         # Modelos SQLAlchemy
│   ├── database.py       # Config de BD
│   ├── routers/         # Routes API
│   ├── services/        # Lógica de negocio
│   └── static/          # Archivos estáticos
├── data/                # Imágenes y audios
├── requirements.txt
└── README.md
```

## Desarrollo

### Regenerar modelos (si hay cambios)

```bash
pip install sqlalchemy
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

## Licencia

MIT License - Ver archivo LICENSE.