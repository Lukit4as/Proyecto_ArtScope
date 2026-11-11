import numpy as np
import cv2

from app.core.imaging import load_image_cv2
from app.core.operations import adjust_brightness


# 1. Cargar la imagen original
image = load_image_cv2("examples/pintura1.jpg")

# 2. Aplicar diferentes niveles de brillo
bright_image = adjust_brightness(image, 50)
dark_image = adjust_brightness(image, -50)
original_brightness = adjust_brightness(image, 0)

# 3. Guardar los resultados
cv2.imwrite("outputs/pintura_bright.png", bright_image)
cv2.imwrite("outputs/pintura_dark.png", dark_image)
cv2.imwrite("outputs/pintura_brightness_original.png", original_brightness)

# 4. Mostrar información
print("AJUSTE DE BRILLO")

print("Dimensiones originales:", image.shape)
print("Dimensiones procesadas:", bright_image.shape)

print("Brillo original - píxel:", image[0, 0])
print("Brillo aumentado - píxel:", bright_image[0, 0])
print("Brillo reducido - píxel:", dark_image[0, 0])

print("Imagen original conservada:", image is not bright_image)
print("Procesamiento completado.")

# 5. Validaciones del procesamiento

print("\nVALIDACIONES")

print(
    "Dimensiones conservadas:",
    image.shape == bright_image.shape
)

print(
    "Valores dentro del rango:",
    bright_image.min() >= 0 and bright_image.max() <= 255
)

print(
    "Imagen original sin modificaciones:",
    np.array_equal(
        image,
        load_image_cv2("examples/pintura1.jpg")
    )
)

print(
    "Beta 0 conserva la imagen:",
    np.array_equal(image, original_brightness)
)