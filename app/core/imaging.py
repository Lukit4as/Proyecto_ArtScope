"""
imaging.py

Funciones básicas para cargar y describir imágenes digitales en el proyecto ArtScope.
"""

from pathlib import Path

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
