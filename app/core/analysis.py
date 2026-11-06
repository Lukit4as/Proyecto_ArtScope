"""
analysis.py

Funciones de análisis de imágenes para ArtScope
"""

import cv2
import numpy as np


def calculate_color_histograms(image: np.ndarray) -> dict:
    """
    Calcula los histogramas de los canales BGR de una imagen

    Args:
        image: Imagen representada en formato BGR.
    
    Returns:
        dict: Histogramas de los canales azul, verde y rojo
    Raises:
        ValueError: Si la imagen no tiene tres canales.
        TypeError: Si la entrada no es un array NumPy
    """

    if not isinstance(image, np.ndarray):
        raise TypeError(
            "La imagen debe ser un array de NumPy"
        )

    if image.ndim != 3 or image.shape[2] != 3: 
        raise ValueError(
            "La imagen debe tener tres canales de color"
        )

    histograms = {}

    channels = {
        "blue": 0,
        "green": 1,
        "red": 2
    }

    for channel_name, channel_index in channels.items():

        histogram = cv2.calcHist(
            [image],
            [channel_index],
            None,
            [256],
            [0, 256]
        )

        histograms[channel_name] = histogram.flatten()

    return histograms

def calculate_grayscale_histogram(image: np.ndarray) -> dict:
    """
    Calcula el histograma y estadísticas de luminosidad de una imagen en escala de grises.

    Args:
        image: Imagen representada en escala de grises

    Returns:
        dict: Histograma y estadística de luminosidad.
    """

    if not isinstance(image, np.ndarray):
        raise TypeError(
            "La imagen debe ser un array de NumPy"
        )

    if image.ndim !=2:
        raise ValueError(
            "La imagen debe estar en escala de grises"
        )

    histogram = cv2.calcHist(
        [image],
        [0],
        [256],
        [0, 256],
    ).flatten()

    return {
        "histogram": histogram,
        "minimum": int(image.min()),
        "maximum": int(image.max()),
        "mean": float(image.mean())
    }
