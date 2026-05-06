import os
import asyncio
from pathlib import Path
import edge_tts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NARRATIONS_DIR = os.path.join(BASE_DIR, "app", "static", "narraciones")
os.makedirs(NARRATIONS_DIR, exist_ok=True)

VOICE = "es-CO-SalomeNeural"


async def generate_audio(text: str, poi_id: int) -> str:
    if not text or not text.strip():
        return ""

    filename = f"{poi_id}.mp3"
    filepath = os.path.join(NARRATIONS_DIR, filename)

    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filepath)

    return filename


def generate_audio_sync(text: str, poi_id: int) -> str:
    return asyncio.run(generate_audio(text, poi_id))
