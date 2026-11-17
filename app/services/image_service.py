
"""
image_service.py

Servicios de carga, procesamiento, análisis y restauración
de imágenes para ArtScope.
"""

import base64
import binascii
from io import BytesIO

import cv2
import numpy as np

from PIL import Image, UnidentifiedImageError

from app.core import restoration
from app.core import operations
from app.core import imaging
from app.core import analysis
from app.core.storage import FileStorage
from app import schemas
from app import config


# ========================================
# PROCESAMIENTO DE IMÁGENES
# ========================================

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


# ========================================
# CARGA DE IMÁGENES
# ========================================

def upload_image(image_bytes: bytes):
    """
    Valida, decodifica, guarda y describe una imagen recibida.
    """

    if not isinstance(image_bytes, bytes):
        raise TypeError("El contenido debe ser de tipo bytes.")

    if not image_bytes:
        raise ValueError("El archivo está vacío.")

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
        raise ValueError(
            "El archivo no contiene una imagen válida."
        ) from error

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


# ========================================
# PROCESAMIENTO DE IMÁGENES ALMACENADAS
# ========================================

def process_stored_image(
    file_name: str,
    operation: str,
    parameters: dict | None = None
):
    """
    Recupera una imagen almacenada, aplica una operación
    y guarda el resultado como una nueva imagen PNG.
    """

    storage = FileStorage()

    image_bytes = storage.read(file_name)

    image = imaging.decode_image_bytes(image_bytes)

    processed_image = apply_image_operation(
        image,
        operation,
        parameters
    )

    success, encoded_image = cv2.imencode(
        ".png",
        processed_image
    )

    if not success:
        raise ValueError(
            "No se pudo codificar la imagen procesada."
        )

    stored_file = storage.save(
        encoded_image.tobytes(),
        "PNG"
    )

    return schemas.StoredImageResponse(
        file_name=stored_file.file_name,
        url=stored_file.url,
        size_bytes=stored_file.size_bytes
    )


# ========================================
# ANÁLISIS DE IMÁGENES
# ========================================

def analyze_stored_image(file_name: str):
    """
    Calcula histogramas de color y estadísticas
    de luminosidad de una imagen almacenada.
    """

    storage = FileStorage()

    image_bytes = storage.read(file_name)

    image = imaging.decode_image_bytes(image_bytes)

    color_histograms = analysis.calculate_color_histograms(image)

    grayscale_image = imaging.convert_to_grayscale(image)

    grayscale_histogram = analysis.calculate_grayscale_histogram(
        grayscale_image
    )

    return {
        "color_histograms": {
            channel: histogram.flatten().tolist()
            for channel, histogram in color_histograms.items()
        },
        "grayscale": {
            "histogram": grayscale_histogram["histogram"].tolist(),
            "minimum": grayscale_histogram["minimum"],
            "maximum": grayscale_histogram["maximum"],
            "mean": grayscale_histogram["mean"]
        }
    }


# ========================================
# DETECCIÓN DE BORDES
# ========================================

def detect_stored_image_edges(
    file_name: str,
    threshold1: int = 100,
    threshold2: int = 200
):
    """
    Detecta los bordes de una imagen almacenada
    mediante el algoritmo Canny.
    """

    storage = FileStorage()

    image_bytes = storage.read(file_name)

    image = imaging.decode_image_bytes(image_bytes)

    grayscale_image = imaging.convert_to_grayscale(image)

    edges = analysis.detect_edges(
        grayscale_image,
        threshold1,
        threshold2
    )

    success, encoded_image = cv2.imencode(
        ".png",
        edges
    )

    if not success:
        raise ValueError(
            "No se pudo codificar la imagen de bordes."
        )

    stored_file = storage.save(
        encoded_image.tobytes(),
        "PNG"
    )

    return schemas.StoredImageResponse(
        file_name=stored_file.file_name,
        url=stored_file.url,
        size_bytes=stored_file.size_bytes
    )


# ========================================
# DECODIFICACIÓN DE LA MÁSCARA
# ========================================

def decode_restoration_mask(
    mask_base64: str,
    expected_shape: tuple
) -> np.ndarray:
    """
    Decodifica una máscara PNG enviada en Base64.

    La máscara debe tener las mismas dimensiones que
    la imagen original.

    Los píxeles seleccionados se convierten en 255
    y los restantes en 0.
    """

    if not isinstance(mask_base64, str) or not mask_base64:
        raise ValueError("No se recibió una máscara válida.")

    # Permitir tanto Base64 puro como una Data URL.
    if "," in mask_base64:
        mask_base64 = mask_base64.split(",", 1)[1]

    try:
        mask_bytes = base64.b64decode(
            mask_base64,
            validate=True
        )

    except (binascii.Error, ValueError) as error:
        raise ValueError(
            "La máscara no tiene un formato Base64 válido."
        ) from error

    if not mask_bytes:
        raise ValueError("La máscara está vacía.")

    # Decodificar la máscara como imagen en escala de grises.
    mask_array = np.frombuffer(
        mask_bytes,
        dtype=np.uint8
    )

    mask = cv2.imdecode(
        mask_array,
        cv2.IMREAD_GRAYSCALE
    )

    if mask is None:
        raise ValueError(
            "No se pudo interpretar la imagen de la máscara."
        )

    # Comprobar que coincida con las dimensiones originales.
    if mask.shape != expected_shape:
        raise ValueError(
            "La máscara debe tener las mismas dimensiones "
            "que la imagen original."
        )

    # Convertir todos los píxeles seleccionados a 255.
    _, binary_mask = cv2.threshold(
        mask,
        10,
        255,
        cv2.THRESH_BINARY
    )

    if not np.any(binary_mask):
        raise ValueError(
            "La máscara no contiene ninguna zona seleccionada."
        )

    return binary_mask


# ========================================
# RESTAURACIÓN DE IMÁGENES
# ========================================

def restore_stored_image(
    file_name: str,
    technique: str,
    parameters: dict | None = None
):
    """
    Recupera una imagen almacenada, aplica una técnica
    de restauración y guarda el resultado como PNG.

    Técnicas disponibles:
    - denoise
    - color-correction
    - detail-enhancement
    - inpainting
    """

    if parameters is None:
        parameters = {}

    if not isinstance(parameters, dict):
        raise TypeError(
            "Los parámetros deben enviarse como un objeto."
        )

    parameters = parameters.copy()

    storage = FileStorage()

    # 1. Recuperar la imagen original.
    image_bytes = storage.read(file_name)

    # 2. Decodificar la imagen en formato BGR.
    image = imaging.decode_image_bytes(image_bytes)

    # 3. Seleccionar la técnica.
    available_techniques = {
        "denoise": restoration.reduce_noise,
        "color-correction": restoration.correct_color,
        "detail-enhancement": restoration.enhance_details
    }

    # 4. Ejecutar la técnica correspondiente.
    if technique == "inpainting":

        # Recuperar la máscara enviada por el frontend.
        mask_base64 = parameters.pop(
            "mask_base64",
            None
        )

        if mask_base64 is None:
            raise ValueError(
                "Es necesario seleccionar una zona de la pintura."
            )

        mask = decode_restoration_mask(
            mask_base64,
            image.shape[:2]
        )

        # Parámetros propios de Inpainting.
        radius = parameters.pop("radius", 3.0)
        method = parameters.pop("method", "telea")

        if parameters:
            raise ValueError(
                "Se recibieron parámetros no válidos para Inpainting."
            )

        restored_image = restoration.reconstruct_damage(
            image,
            mask,
            radius=radius,
            method=method
        )

    elif technique in available_techniques:

        restored_image = available_techniques[technique](
            image,
            **parameters
        )

    else:

        raise ValueError(
            f"Técnica de restauración no disponible: {technique}"
        )

    # 5. Codificar el resultado como PNG.
    success, encoded_image = cv2.imencode(
        ".png",
        restored_image
    )

    if not success:
        raise ValueError(
            "No se pudo codificar la imagen restaurada."
        )

    # 6. Guardar una nueva imagen.
    # El archivo original permanece intacto.
    stored_file = storage.save(
        encoded_image.tobytes(),
        "PNG"
    )

    return schemas.StoredImageResponse(
        file_name=stored_file.file_name,
        url=stored_file.url,
        size_bytes=stored_file.size_bytes
    )
