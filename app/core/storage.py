import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from app import config

CHUNK_SIZE = 1024 * 1024

EXTENSIONS = {
    "PNG": ".png",
    "JPEG": ".jpeg",
    "WEBP": ".webp",
    "BMP": ".bmp"
}

def read_upload(
        stream: BinaryIO,
        max_bytes: int = config.MAX_SIZE_BYTES
) -> bytes:
    """
    Lee un archivo por bloques y controla su tamaño.
    """
    buffer = bytearray()

    while chunk := stream.read(CHUNK_SIZE):
        buffer.extend(chunk)

        if len(buffer) > max_bytes:
            raise ValueError("El archivo supera el tamaño permitido.")

    return bytes(buffer)


@dataclass(frozen=True)
class StoredFile:
    file_name: str
    url: str
    size_bytes: int

class FileStorage:

    def __init__(self, directory: Path | None = None):
        self._directory = directory or config.STORAGE_DIR
        self._directory.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, image_format: str) -> StoredFile:

        if image_format not in EXTENSIONS:
            raise ValueError("Formato de archivo no permitido")

        file_name = uuid.uuid4().hex + EXTENSIONS[image_format]

        self.path(file_name).write_bytes(content)

        return StoredFile(
            file_name=file_name,
            url=f"{config.MEDIA_URL}/{file_name}",
            size_bytes=len(content)
        )
    def read(self, file_name: str)-> bytes:
        return self.path(file_name).read_bytes()

    def delete(self, file_name: str) -> None:
        self.path(file_name).unlink(missing_ok=True)

    def path(self, file_name: str) -> Path:

        if Path(file_name).name != file_name:
            raise ValueError("Nombre de archivo inválido.")

        return self._directory / file_name 




