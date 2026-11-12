"""
imaging.py

Funciones básicas para cargar y describir imágenes digitales en el proyecto ArtScope.
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

def load_image(image_path: str) -> Image.Image:
    """
    Carga una imagen desde una ruta y devuelve un objeto de Pillow.

    Args:
        image_path: Ruta del archivo de imagen.

    Returns:
        Image.Image: Imagen cargada.

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no es una imágen valida.
    """

    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    try:
        with Image.open(path) as image:
            image.load()
            loaded_image = image.copy()
            loaded_image.format = image.format
        
            return loaded_image
        

    except (UnidentifiedImageError, OSError) as error:
        raise ValueError(
            f"No se pudo cargar la imagen: {path}"
        )    from error

def get_image_info(image: Image.Image) -> dict:
        """
        Obtiene información técnica de una imagen.

        Args:
            image: Imagen cargada mediante Pillow

        Returns:
            dict: Información sobre dimensiones, formato, modo de color y representación NumPy.
        """
        image_array = np.asarray(image)

        return {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "shape": image_array.shape,
            "dtype": str(image_array.dtype),
            "channels": (
                1 if image_array.ndim == 2
                else image_array.shape[2]
            ),
            "memory_bytes": image_array.nbytes,
        }    

def get_pixel(image: Image.Image, x: int, y:int):
    """
    Obtiene el valor de un píxel según sus coordenadas.

    Args:
        image: Imagen cargada mediante Pillow.
        x: Coordenada horizontal.
        y: Coordenada vertical.
    Returns: 
        Valor del píxel seleccionado.
    """

    if not (0 <= x < image.width and 0 <= y< image.height):
     raise ValueError(
         f"Coordenadas fuera de rango: ({x}, {y})"
     )

    image_array = np.asarray(image)

    return image_array[y, x] 

def load_image_cv2(image_path: str) -> np.ndarray:
    """
    Carga una imagen utilizando OpenCV.
    La imagen se devuelve en formato BGR.

    Args:
        image_path: Ruta del archivo de imagen.

    Returns:
        np.ndarray: Imagen representada como matriz NumPy.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si OpenCV no puede interpretar la imagen.
    """
    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"No se encontró el archivo: {path}"
        )

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(
            f"No se pudo cargar la imagen: {path}"
        )
    
    return image

def convert_bgr_to_rgb(image: np.ndarray) -> np.ndarray:

    """
    Convierte una imagen del formato BGR al formato RGB.

    Args:
        image: Imagen representada en formato BGR.

    Returns:
        np.ndarray: Imagen convertida al formato RGB.

    Raises:
        ValueError: Si la imagen no tiene tres canales.
    """

    if not isinstance(image, np.ndarray):
        raise TypeError(
            "La imagen debe ser un array de NumPy"
        )

    if image.ndim != 3 or image .shape[2] !=3:
        raise ValueError(
            "La imagen debe tener tres canales de color"
        )

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convierte una imagen BGR a escala de grises.

    Args:
        image: Imagen representada en formato BGR
    
    Returns:
        np.ndarray: Imagen de un solo canal en escala de grises.
    
    Raises:
        ValueError: Si la imagen no tiene tres canales

    """

    if not isinstance(image, np.ndarray):
        raise TypeError(
            "La imagen debe ser un array de NumPy."
        )

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(
            "La imagen debe tener tres canales de color."
        )

    grayscale_image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return grayscale_image

def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Decodifica una imagen recibida como bytes y la convierte en un array de NumPy en formato BGR.

    Args:
        image_bytes: Contenido binatio de la imagen.
    
    Returns:
        np.ndarray: Imagen decodificada en formato BGR.
    
    Raises: 
        TypeError: Si la entrada no es de tipo bytes.
        ValueError: Si los bytes están vacíos o no representan una imagen válida.
    """

    if not isinstance(image_bytes, bytes):
        raise TypeError(
            "La imagen debe recibirse en formato bytes."
        )

    if not image_bytes:
        raise ValueError(
            "El archivo recibido esta vacío."
        )

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            "No se pudo decodificar la imagen."
        )

    return image