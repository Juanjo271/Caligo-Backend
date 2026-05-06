import os
from pathlib import Path
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_IMAGES_DIR = os.path.join(BASE_DIR, "app", "static", "ref_images")
os.makedirs(REF_IMAGES_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def save_image(file_content: bytes, original_filename: str, poi_id: int) -> Optional[str]:
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None

    if len(file_content) > MAX_FILE_SIZE:
        return None

    filename = f"{poi_id}{ext}"
    filepath = os.path.join(REF_IMAGES_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file_content)

    return filename


def delete_image(poi_id: int) -> bool:
    for ext in ALLOWED_EXTENSIONS:
        filepath = os.path.join(REF_IMAGES_DIR, f"{poi_id}{ext}")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    return False


def get_image_path(poi_id: int) -> Optional[str]:
    for ext in ALLOWED_EXTENSIONS:
        filepath = os.path.join(REF_IMAGES_DIR, f"{poi_id}{ext}")
        if os.path.exists(filepath):
            return filepath
    return None
