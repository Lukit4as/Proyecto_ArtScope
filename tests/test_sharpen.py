
import numpy as np
import cv2

from app.core.imaging import load_image_cv2
from app.core.operations import apply_sharpen


# Cargar imagen original
image = load_image_cv2("examples/pintura1.jpg")

# Aplicar enfoque
sharpened_image = apply_sharpen(image)

# Guardar resultado
cv2.imwrite("outputs/pintura_sharpen.png", sharpened_image)


print("ENFOQUE (SHARPEN)")
print("Dimensiones originales:", image.shape)
print("Dimensiones procesadas:", sharpened_image.shape)
print("Pixel original:", image[0, 0])
print("Pixel enfocado:", sharpened_image[0, 0])

print("\nVALIDACIONES")

print(
    "Dimensiones conservadas:",
    image.shape == sharpened_image.shape
)

print(
    "Valores dentro del rango:",
    sharpened_image.min() >= 0 and sharpened_image.max() <= 255
)

print(
    "Imagen original conservada:",
    np.array_equal(image, load_image_cv2("examples/pintura1.jpg"))
)

print(
    "Resultado diferente al original:",
    not np.array_equal(image, sharpened_image)
)

print("\nProcesamiento completado.")
