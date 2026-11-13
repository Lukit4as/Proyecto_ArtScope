from io import BytesIO

import cv2

from PIL import Image, UnidentifiedImageError

from app.core import operations
from app.core import imaging
from app.core.storage import FileStorage
from app import schemas
from app import config


def apply_image_operation(
        image,
        operation: str,
        parameters: dict | None = None
):
    if parameters is None:
        parameters = {}

    available_operations = {
        "brightness": operations.adjust_brightness,
        "contrast": operations.adjust_contrast,
        "blur": operations.apply_gaussian_blur,
        "sharpen": operations.apply_sharpen,
        "rotation": operations.rotate_image,
        "resize": operations.resize_image
    }

    if operation not in available_operations:
        raise ValueError(f"Operación no disponible: {operation}")

    selected_operation = available_operations[operation]

    return selected_operation(image, **parameters)

def upload_image(image_bytes: bytes):
    """
    Valida, decodifica, guarda y describe una imagen recibida.
    """
    if not isinstance(image_bytes, bytes):
        raise TypeError("El contenido debe ser de tipo bytes.")

    if not image_bytes:
        raise ValueError("El archivo esta vacío.")

    if len(image_bytes) > config.MAX_SIZE_BYTES:
        raise ValueError("El archivo supera el tamaño máximo permitido.")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image_format = image.format

            if image_format not in config.ALLOWED_FORMATS:
                raise ValueError("Formato de imagen no permitido.")

            image.verify()

        decoded_image = imaging.decode_image_bytes(image_bytes)

        with Image.open(BytesIO(image_bytes)) as image:
            image_info = imaging.get_image_info(image)
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("El archivo no contiene una imagen válida.") from error

    storage = FileStorage()

    stored_file = storage.save(
        image_bytes,
        image_format
    )

    return {
        "stored_image": schemas.StoredImageResponse(
            file_name=stored_file.file_name,
            url=stored_file.url,
            size_bytes=stored_file.size_bytes
        ),
        "image_info": schemas.ImageInfoResponse(**image_info),
        "image": decoded_image
    }

def process_stored_image(
        file_name: str,
        operation: str,
        parameters: dict | None = None
):
    """
    Recupera una imagen almacenada, aplica una operación y guarda el resultado como una nueva imagen PNG.
    """

    storage = FileStorage()

    # 1. Recuperar los bytes de la imagen original
    image_bytes = storage.read(file_name)

    # 2. Convertir los bytes en una matriz OpenCV
    image = imaging.decode_image_bytes(image_bytes)

    # 3. Ejecutar la operación solicitada
    processed_image = apply_image_operation(
        image,
        operation,
        parameters
    )

    # 4. Codificar el resultado como PNG
    success, encoded_image = cv2.imencode(
        ".png",
        processed_image
    )

    if not success:
        raise ValueError("No se pudo codificar la imagen procesada.")

    # 5. Guardar la nueva imagen
    stored_file = storage.save(
        encoded_image.tobytes(),
        "PNG"
    )

    return schemas.StoredImageResponse(
        file_name=stored_file.file_name,
        url=stored_file.url,
        size_bytes=stored_file.size_bytes
    )
