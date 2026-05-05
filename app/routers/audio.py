from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NARRACIONES_DIR = os.path.join(BASE_DIR, "app", "static", "narraciones")

router = APIRouter(prefix="/api/audio", tags=["Audio"])


@router.get("/{filename}")
def get_audio(filename: str):
    if not filename.endswith(".mp3"):
        filename = f"{filename}.mp3"

    file_path = os.path.join(NARRACIONES_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Audio no encontrado: {filename}")

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename,
    )
