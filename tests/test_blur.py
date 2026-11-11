import cv2
import numpy as np

from app.core.imaging import load_image_cv2
from app.core.operations import apply_gaussian_blur

# 1. Cargar la imagen original
image = load_image_cv2("examples/pintura1.jpg")

# 2. Aplicar diferentes niveles de desenfoque
blur_3 = apply_gaussian_blur(image, 3)
blur_5 = apply_gaussian_blur(image, 5)
blur_7 = apply_gaussian_blur(image, 7)

# 3. Guardar las imágenes procesadas
cv2.imwrite("outputs/pintura_blur_3.png", blur_3)
cv2.imwrite("outputs/pintura_blur_5.png", blur_5)
cv2.imwrite("outputs/pintura_blur_7.png", blur_7)

# 4. Mostrar información
print("DESENFOQUE GAUSSIANO")

print("Dimensiones originales:", image.shape)
print("Dimensiones procesadas:", blur_5.shape)

print("Pixel original:", image[0, 0])
print("Pixel con kernel 3:", blur_3[0, 0])
print("Pixel con kernel 5:", blur_5[0, 0])
print("Pixel con kernel 7:", blur_7[0, 0])

# 5. Validaciones
print("\nVALIDACIONES")

print(
    "Dimensiones conservadas:",
    image.shape == blur_5.shape
)

print(
    "Valores dentro del rango:",
    blur_5.min() >= 0 and blur_5.max() <= 255
)

print(
    "Imagen original conservada:",
    np.array_equal(
        image,
        load_image_cv2("examples/pintura1.jpg")
    )
)

print(
    "El resultado es diferente al original:",
    not np.array_equal(image, blur_5)
)

print("Procesamiento completado.")

print("\nCOMPARACIÓN DE DESENFOQUE")

print(
    "Diferencia kernel 3:",
    np.mean(np.abs(image.astype(float) - blur_3.astype(float)))
)

print(
    "Diferencia kernel 5:",
    np.mean(np.abs(image.astype(float) - blur_5.astype(float)))
)

print(
    "Diferencia kernel 7:",
    np.mean(np.abs(image.astype(float) - blur_7.astype(float)))
)