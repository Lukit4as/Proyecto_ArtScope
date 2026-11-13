from pathlib import Path

from app.services.image_service import upload_image
from app.core.storage import FileStorage

print("PRUEBA DE CARGA DE IMÁGENES")


# 1. Leer la imagen original como bytes
image_path = Path("examples/pintura1.jpg")
image_bytes = image_path.read_bytes()

# 2. Ejecutar el servicio
result = upload_image(image_bytes)

stored_image = result["stored_image"]
image_info = result["image_info"]
decoded_image = result["image"]

try:
    # 3. Comprobar los resultados
    print("Nombre:", stored_image.file_name)
    print("URL:", stored_image.url)
    print("Tamaño:", stored_image.size_bytes)

    print("Dimensiones:", decoded_image.shape)
    print("Formato:", image_info.format)
    print("Canales:", image_info.channels)

    assert stored_image.size_bytes == len(image_bytes)
    assert decoded_image.shape == (640, 429, 3)
    assert image_info.format == "JPEG"
    assert image_info.width == 429
    assert image_info.height == 640

    # 4. Comprobar que el archivo realmente existe

    storage = FileStorage()
    assert storage.path(stored_image.file_name).is_file()

    print("Guardado:", "correcto")
    print("Información técnica:", "correcta")
    print("Decodificación:", "correcta")

finally:
    # 5. Limpiar el archivo de prueba
    FileStorage().delete(stored_image.file_name)

print("\nTodas las pruebas fueron exitosas.")