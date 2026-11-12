from pathlib import Path
import numpy as np

from app.core.imaging import(
    load_image_cv2,
    decode_image_bytes
)

# 1. Leer una imagen como bytes
image_path = Path("examples/pintura1.jpg")
image_bytes = image_path.read_bytes()

# 2. Decodificar los bytes
decoded_image = decode_image_bytes(image_bytes)

# 3. Cargar la misma imagen directamente con OpenCV
original_image = load_image_cv2(str(image_path))

# 4. Comprobar resultados
print("PRUEBA DE DECODIFICACIÓN")

print("Tipo de entrada:", type(image_bytes))
print("Tipo de salida:", type(decoded_image))
print("Dimensiones:", decoded_image.shape)
print("Tipo de datos:", decoded_image.dtype)

print(
    "Imagenes iguales:",
    np.array_equal(decoded_image, original_image)
)

# 5. Validaciones automáticas
assert isinstance(decoded_image, np.ndarray)
assert decoded_image.shape == original_image.shape
assert np.array_equal(decoded_image, original_image)

try:
    decode_image_bytes(b"")
except ValueError:
    print("Validación de contenido vacío: correcta")

try:
    decode_image_bytes(b"esto no es una imagen")
except ValueError:
    print("Validación de imagen inválida: correcta")

print("\nTodas las pruebas fueron exitosas.")
