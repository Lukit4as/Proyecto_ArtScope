
"""
restoration.py

Funciones de restauración digital de pinturas para ArtScope.

El objetivo es mejorar la apariencia visual de una obra
preservando sus colores, bordes, pinceladas y texturas.
"""

import cv2
import numpy as np


def validate_image(image: np.ndarray) -> None:
    """
    Valida que la imagen sea un array NumPy BGR de tipo uint8.
    """

    if not isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    if image.dtype != np.uint8:
        raise ValueError("La imagen debe tener valores uint8.")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales BGR.")


def reduce_noise(
    image: np.ndarray,
    diameter: int = 7,
    sigma_color: float = 35,
    sigma_space: float = 35
) -> np.ndarray:
    """
    Reduce el ruido mediante un filtro bilateral.

    Preserva mejor los bordes que un suavizado convencional.
    """

    validate_image(image)

    if diameter <= 0:
        raise ValueError("El diámetro debe ser positivo.")

    if sigma_color <= 0 or sigma_space <= 0:
        raise ValueError("Los parámetros sigma deben ser positivos.")

    restored = cv2.bilateralFilter(
        image,
        diameter,
        sigma_color,
        sigma_space
    )

    return restored


def correct_color(
    image: np.ndarray,
    clip_limit: float = 1.5,
    tile_grid_size: int = 8
) -> np.ndarray:
    """
    Mejora el contraste local y la iluminación utilizando LAB y CLAHE.

    Se modifica principalmente el canal de luminosidad,
    procurando conservar la información cromática.
    """

    validate_image(image)

    if clip_limit <= 0:
        raise ValueError("El límite de contraste debe ser positivo.")

    if tile_grid_size <= 0:
        raise ValueError("El tamaño de la cuadrícula debe ser positivo.")

    lab_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    lightness, channel_a, channel_b = cv2.split(lab_image)

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(tile_grid_size, tile_grid_size)
    )

    corrected_lightness = clahe.apply(lightness)

    corrected_lab = cv2.merge(
        (corrected_lightness, channel_a, channel_b)
    )

    corrected_image = cv2.cvtColor(
        corrected_lab,
        cv2.COLOR_LAB2BGR
    )

    return corrected_image


def enhance_details(
    image: np.ndarray,
    strength: float = 0.35,
    sigma: float = 1.0
) -> np.ndarray:
    """
    Realza detalles mediante una máscara de enfoque suave.

    Combina la imagen original con una versión desenfocada
    para resaltar detalles y conservar la estructura original.
    """

    validate_image(image)

    if not 0 <= strength <= 1:
        raise ValueError("La intensidad debe estar entre 0 y 1.")

    if sigma <= 0:
        raise ValueError("Sigma debe ser positivo.")

    blurred = cv2.GaussianBlur(
        image,
        (0, 0),
        sigma
    )

    enhanced = cv2.addWeighted(
        image,
        1.0 + strength,
        blurred,
        -strength,
        0
    )

    return enhanced


def reconstruct_damage(
    image: np.ndarray,
    mask: np.ndarray,
    radius: float = 3.0,
    method: str = "telea"
) -> np.ndarray:
    """
    Reconstruye regiones seleccionadas mediante inpainting.

    La máscara debe indicar con valores distintos de cero
    las zonas que se desean reconstruir.
    """

    validate_image(image)

    if not isinstance(mask, np.ndarray):
        raise TypeError("La máscara debe ser un array de NumPy.")

    if mask.ndim != 2:
        raise ValueError("La máscara debe ser de un solo canal.")

    if mask.shape != image.shape[:2]:
        raise ValueError("La máscara debe tener las dimensiones de la imagen.")

    if radius <= 0:
        raise ValueError("El radio debe ser positivo.")

    methods = {
        "telea": cv2.INPAINT_TELEA,
        "ns": cv2.INPAINT_NS
    }

    if method not in methods:
        raise ValueError("Método de reconstrucción no disponible.")

    reconstructed = cv2.inpaint(
        image,
        mask.astype(np.uint8),
        radius,
        methods[method]
    )

    return reconstructed
