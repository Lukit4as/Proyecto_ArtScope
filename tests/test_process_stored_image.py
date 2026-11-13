from pathlib import Path

import numpy as np

from app.services.image_service import (
    upload_image,
    process_stored_image
)
from app.core.storage import FileStorage
from app.core.imaging import decode_image_bytes

print("PRUEBA DE PROCESAMIENTO DE IMÁGENES")

storage = FileStorage()

# 1. Cargar la imagen original
image_path = Path("examples/pintura1.jpg")
image_bytes = image_path.read_bytes()

# 2. Guardarla mediante nuestro servicio

upload_result = upload_image(image_bytes)
original_file = upload_result["stored_image"]

processed_file = None

try:
    # 3. Procesar la imagen aumentando el brillo
    processed_file = process_stored_image(
        original_file.file_name,
        "brightness",
        {"beta":50}
    )
    # 4. Recuperar ambas imágenes
    original_bytes = storage.read(original_file.file_name)
    processed_bytes = storage.read(processed_file.file_name)

    original_image = decode_image_bytes(original_bytes)
    processed_image = decode_image_bytes(processed_bytes)


    # 5. Comprobar resultados
    print("Archivo original:", original_file.file_name)
    print("Archivo procesado:", processed_file.file_name)
    print("Tamaño original:", len(original_bytes))
    print("Tamaño procesado:", len(processed_bytes))

    print("Dimensiones originales:", original_image.shape)
    print("Dimensiones procesadas:", processed_image.shape)

    print(
        "Imagen modificada:",
        not np.array_equal(original_image, processed_image)
    )
    print(
        "Original conservado:",
        np.array_equal(
            original_image,
            decode_image_bytes(original_bytes)
        )
    )

    # 6. Validaciones
    assert original_image.shape == processed_image.shape
    assert not np.array_equal(original_image, processed_image)
    assert processed_file.file_name != original_file.file_name
    assert processed_file.file_name.endswith(".png")
    assert storage.path(original_file.file_name).is_file()
    assert storage.path(processed_file.file_name).is_file()

    print("\nTodas las pruebas fueron exitosas.")

finally:
    # 7. Eliminar los archivos de prueba
    storage.delete(original_file.file_name)

    if processed_file is not None:
        storage.delete(processed_file.file_name)