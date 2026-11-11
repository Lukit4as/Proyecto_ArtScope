import cv2
import numpy as np

def adjust_brightness(image: np.ndarray, beta: float = 0) -> np.ndarray:
    """
    Modifica el brillo de una imagen.

    Args:
        image: Imagen representada como matriz NumPy.
        beta: Cantidad de brillo que se agrega o se resta.
    
        Returns:
            Una nueva imagen con el brillo modificado.
    """

    # Validar que la entrada sea una matriz NumPy
    if not  isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    # Validar que sea una imagen a color BGR
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales de color.")

    # Validar el parámetro de brillo
    if not isinstance(beta,(int, float)) or isinstance(beta, bool):
        raise TypeError("El brillo debe ser un número.")

    # Convertir a un tipo numérico que permita valores negativos
    image_float = image.astype(np.float32)

    # Aplicar el ajuste de brillo
    adjusted_image = image_float + beta

    # Limitar los valores al rango permitido
    adjusted_image = np.clip(adjusted_image, 0, 255)

    # Convertir nuevamente a uint8
    adjusted_image = adjusted_image.astype(np.uint8)

    return adjusted_image


def adjust_contrast(image: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """
    Modifica el contraste de una imagen.

    Args:
        image: Imagen representada como matriz NumPy.
        alpha: Factor de contraste.

    Returns:
        Una nueva imagen con el contraste modificado.
    """

    # Validar que la entrada sea una matriz NumPy
    if not isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    # Validar que sea una imagen a color BGR
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales de color.")

    # Validar el factor de contraste
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool):
        raise TypeError("El contraste debe ser un número.")

    if alpha < 0:
        raise ValueError("El factor de contraste no puede ser negativo.")

    # Convertir la imagen a float32
    image_float = image.astype(np.float32)

    # Aplicar el ajuste de contraste
    adjusted_image = 128 + alpha * (image_float - 128)

    # Limitar los valores al rango permitido
    adjusted_image = np.clip(adjusted_image, 0, 255)

    # Convertir nuevamente a uint8
    adjusted_image = adjusted_image.astype(np.uint8)

    return adjusted_image


def apply_gaussian_blur(
    image: np.ndarray,
    kernel_size: int = 5
) -> np.ndarray:
    """
    Aplica un desenfoque Gaussiano a una imagen.

    Args:
        image: Imagen representada como matriz NumPy.
        kernel_size: Tamaño del núcleo del filtro.

    Returns:
        Una nueva imagen desenfocada.
    """

    if not isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales de color.")

    if not isinstance(kernel_size, int) or isinstance(kernel_size, bool):
        raise TypeError("El tamaño del kernel debe ser un entero.")

    if kernel_size <= 0 or kernel_size % 2 == 0:
        raise ValueError("El kernel debe ser un número positivo e impar.")

    blurred_image = cv2.GaussianBlur(
        image,
        (kernel_size, kernel_size),
        0
    )

    return blurred_image


def apply_sharpen(image: np.ndarray) -> np.ndarray:
    """
    Aplica un filtro de enfoque a una imagen BGR.

    Resalta los detalles y bordes mediante un kernel espacial.
    Devuelve una nueva imagen sin modificar la original.
    """

    # Validar que el dato recibido sea un array de NumPy
    if not isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    # Validar que sea una imagen de color con tres canales
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales de color.")

    # Definir el kernel de enfoque
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ], dtype=np.float32)

    # Aplicar el filtro espacial
    sharpened_image = cv2.filter2D(
        image,
        -1,
        kernel
    )

    # Devolver la imagen procesada
    return sharpened_image



def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rota una imagen BGR alrededor de su centro.

    Ajusta las dimensiones del lienzo para evitar recortes.
    Devuelve una nueva imagen sin modificar la original.
    """

    # Validar el tipo de dato de entrada
    if not isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    # Validar que sea una imagen de color de tres canales
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales de color.")

    # Validar que el ángulo sea numérico
    if isinstance(angle, bool) or not isinstance(angle, (int, float)):
        raise TypeError("El ángulo debe ser un número.")

    if not np.isfinite(angle):
        raise ValueError("El ángulo debe ser un número finito.")

    # Obtener dimensiones originales
    height, width = image.shape[:2]

    # Calcular el centro de la imagen
    center = (width / 2, height / 2)

    # Crear la matriz de rotación
    rotation_matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    # Calcular el tamaño del nuevo lienzo
    cos_angle = abs(rotation_matrix[0, 0])
    sin_angle = abs(rotation_matrix[0, 1])

    new_width = int(height * sin_angle + width * cos_angle)
    new_height = int(height * cos_angle + width * sin_angle)

    # Ajustar la traslación para centrar la imagen
    rotation_matrix[0, 2] += new_width / 2 - center[0]
    rotation_matrix[1, 2] += new_height / 2 - center[1]

    # Aplicar la transformación geométrica
    rotated_image = cv2.warpAffine(
        image,
        rotation_matrix,
        (new_width, new_height),
        flags=cv2.INTER_LINEAR
    )

    return rotated_image



def resize_image(
    image: np.ndarray,
    width: int,
    height: int,
    interpolation: str = "linear",
    keep_aspect_ratio: bool = False
) -> np.ndarray:
    """
    Redimensiona una imagen BGR.

    Permite elegir el método de interpolación y conservar
    opcionalmente la relación de aspecto original.
    """

    # Validar que la imagen sea un array de NumPy
    if not isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    # Validar que sea una imagen de color de tres canales
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales de color.")

    # Validar ancho y alto
    for dimension in (width, height):
        if isinstance(dimension, bool) or not isinstance(dimension, int):
            raise TypeError("El ancho y el alto deben ser números enteros.")

        if dimension <= 0:
            raise ValueError("El ancho y el alto deben ser positivos.")

    # Validar la opción de mantener proporciones
    if not isinstance(keep_aspect_ratio, bool):
        raise TypeError("keep_aspect_ratio debe ser True o False.")

    # Seleccionar el método de interpolación
    interpolation_methods = {
        "nearest": cv2.INTER_NEAREST,
        "linear": cv2.INTER_LINEAR,
        "cubic": cv2.INTER_CUBIC
    }

    if interpolation not in interpolation_methods:
        raise ValueError(
            "Interpolación inválida. Usar: nearest, linear o cubic."
        )

    # Obtener dimensiones originales
    original_height, original_width = image.shape[:2]

    # Mantener la relación de aspecto si fue solicitado
    if keep_aspect_ratio:
        scale = min(
            width / original_width,
            height / original_height
        )

        new_width = max(1, int(round(original_width * scale)))
        new_height = max(1, int(round(original_height * scale)))
    else:
        new_width = width
        new_height = height

    # Obtener el método de interpolación seleccionado
    method = interpolation_methods[interpolation]

    # Aplicar el redimensionamiento
    resized_image = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=method
    )

    return resized_image

