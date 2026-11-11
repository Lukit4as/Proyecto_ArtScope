
import numpy as np
import cv2

from app.core.imaging import load_image_cv2
from app.core.operations import rotate_image


# Cargar imagen original
image = load_image_cv2("examples/pintura1.jpg")

# Aplicar diferentes rotaciones
rotation_45 = rotate_image(image, 45)
rotation_90 = rotate_image(image, 90)
rotation_180 = rotate_image(image, 180)

# Guardar resultados
cv2.imwrite("outputs/pintura_rotation_45.png", rotation_45)
cv2.imwrite("outputs/pintura_rotation_90.png", rotation_90)
cv2.imwrite("outputs/pintura_rotation_180.png", rotation_180)

print("ROTACIÓN DE IMÁGENES")

print("Dimensiones originales:", image.shape)
print("Dimensiones 45 grados:", rotation_45.shape)
print("Dimensiones 90 grados:", rotation_90.shape)
print("Dimensiones 180 grados:", rotation_180.shape)

print("\nVALIDACIONES")

print(
    "Valores dentro del rango:",
    all(
        result.min() >= 0 and result.max() <= 255
        for result in [rotation_45, rotation_90, rotation_180]
    )
)

print(
    "Imagen original conservada:",
    np.array_equal(image, load_image_cv2("examples/pintura1.jpg"))
)

print(
    "Resultados diferentes al original:",
    all(
        not np.array_equal(image, result)
        for result in [rotation_45, rotation_90, rotation_180]
    )
)

print("\nProcesamiento completado.")
