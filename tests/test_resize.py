
import numpy as np
import cv2

from app.core.imaging import load_image_cv2
from app.core.operations import resize_image


# Cargar imagen original
image = load_image_cv2("examples/pintura1.jpg")

# Redimensionar con distintos métodos
resize_nearest = resize_image(
    image, 320, 480, "nearest"
)

resize_linear = resize_image(
    image, 320, 480, "linear"
)

resize_cubic = resize_image(
    image, 320, 480, "cubic"
)

# Redimensionar conservando la proporción
resize_proportional = resize_image(
    image, 800, 800,
    interpolation="linear",
    keep_aspect_ratio=True
)

# Guardar resultados
cv2.imwrite("outputs/pintura_resize_nearest.png", resize_nearest)
cv2.imwrite("outputs/pintura_resize_linear.png", resize_linear)
cv2.imwrite("outputs/pintura_resize_cubic.png", resize_cubic)
cv2.imwrite("outputs/pintura_resize_proportional.png", resize_proportional)

print("REDIMENSIONAMIENTO DE IMÁGENES")

print("Dimensiones originales:", image.shape)
print("Nearest:", resize_nearest.shape)
print("Linear:", resize_linear.shape)
print("Cubic:", resize_cubic.shape)
print("Proporcional:", resize_proportional.shape)

print("\nVALIDACIONES")

results = [
    resize_nearest,
    resize_linear,
    resize_cubic,
    resize_proportional
]

print(
    "Valores dentro del rango:",
    all(
        result.min() >= 0 and result.max() <= 255
        for result in results
    )
)

print(
    "Imagen original conservada:",
    np.array_equal(image, load_image_cv2("examples/pintura1.jpg"))
)

print(
    "Dimensiones esperadas:",
    resize_nearest.shape == (480, 320, 3)
    and resize_linear.shape == (480, 320, 3)
    and resize_cubic.shape == (480, 320, 3)
)

print(
    "Proporción conservada:",
    abs(
        resize_proportional.shape[1] / resize_proportional.shape[0]
        - image.shape[1] / image.shape[0]
    ) < 0.002
)

print("\nProcesamiento completado.")
