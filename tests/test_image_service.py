import numpy as np

from app.core.imaging import load_image_cv2
from app.services.image_service import apply_image_operation

# 1. Cargar la imagen original
image = load_image_cv2("examples/pintura1.jpg")

# 2. Ejecutar el procesamiento a través del servicio
bright_image = apply_image_operation(
    image,
    "brightness",
    {"beta": 50}
)

# 3. Comprobar los resultados
print("PRUEBA DEL SERVICIO DE IMÁGENES")

print("Dimensiones originales:", image.shape)
print("Dimensiones procesadas:", bright_image.shape)

print("Imagen modificada:", not np.array_equal(image, bright_image))
print("Dimensiones conservadas:", image.shape == bright_image.shape)
print("Tipo de datos conservado:", image.dtype == bright_image.dtype)

print(
    "Imagen original sin modificar:",
    np.array_equal(
        image,
        load_image_cv2("examples/pintura1.jpg")
    )
)

# 4. Validar automáticamente
assert not np.array_equal(image, bright_image)
assert image.shape == bright_image.shape
assert image.dtype == bright_image.dtype
assert np.array_equal(
    image,
    load_image_cv2("examples/pintura1.jpg")
)

print("\nTodas las pruebas fueron exitosas.")