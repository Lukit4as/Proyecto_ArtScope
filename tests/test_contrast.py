
import numpy as np

from app.core.imaging import load_image_cv2
from app.core.operations import adjust_contrast


# 1. Cargar imagen original
image = load_image_cv2("examples/pintura1.jpg")

# 2. Aplicar diferentes factores de contraste
high_contrast = adjust_contrast(image, 1.5)
low_contrast = adjust_contrast(image, 0.5)
original_contrast = adjust_contrast(image, 1.0)

# 3. Mostrar información
print("AJUSTE DE CONTRASTE")

print("Dimensiones originales:", image.shape)
print("Dimensiones procesadas:", high_contrast.shape)

print("Píxel original:", image[0, 0])
print("Píxel con contraste aumentado:", high_contrast[0, 0])
print("Píxel con contraste reducido:", low_contrast[0, 0])

# 4. Guardar imágenes
import cv2

cv2.imwrite("outputs/pintura_contrast_high.png", high_contrast)
cv2.imwrite("outputs/pintura_contrast_low.png", low_contrast)
cv2.imwrite("outputs/pintura_contrast_original.png", original_contrast)

# 5. Validaciones
print("\nVALIDACIONES")

print("Dimensiones conservadas:", image.shape == high_contrast.shape)

print(
    "Valores dentro del rango:",
    high_contrast.min() >= 0 and high_contrast.max() <= 255
)

print(
    "Imagen original conservada:",
    np.array_equal(
        image,
        load_image_cv2("examples/pintura1.jpg")
    )
)

print(
    "Alpha 1 conserva la imagen:",
    np.array_equal(image, original_contrast)
)

print("Procesamiento completado.")
