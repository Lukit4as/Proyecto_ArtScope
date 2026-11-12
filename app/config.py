from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = BASE_DIR / "storage" / "images"

MEDIA_URL = "/media"

ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP", "BMP"}

MAX_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB