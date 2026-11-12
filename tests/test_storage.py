from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from app.core.storage import FileStorage, read_upload

# 1. Leer una imagen de ejemplo
image_path = Path("examples/pintura1.jpg")
image_bytes = image_path.read_bytes()

print("PRUEBA DE ALMACENAMIENTO")

# 2. Probar la lectura por bloques
stream = BytesIO(image_bytes)
read_bytes = read_upload(stream)

assert read_bytes == image_bytes
print("Lectura de bytes: correcta")

# 3. Crear una carpeta temporal para las pruebas
with TemporaryDirectory() as temp_dir:

    storage = FileStorage(Path(temp_dir))

     # 4. Guardar la imagen
    stored = storage.save(read_bytes, "JPEG")

    print("Nombre generado:", stored.file_name)
    print("Tamaño:", stored.size_bytes)

    assert storage.path(stored.file_name).is_file()
    print("Guardado: correcto")

    # 5. Recuperar la imagen
    recovered = storage.read(stored.file_name)

    assert recovered == image_bytes
    print("Recuperación: correcta")

    # 6. Eliminar la imagen
    storage.delete(stored.file_name)

    assert not storage.path(stored.file_name).exists()
    print("Eliminación: correcta")

    # 7. Comprobar el límite de tamaño
    try:
        read_upload(BytesIO(b"123456"), max_bytes=5)
    except ValueError:
        print("Límite de tamaño: correcto")
    else:
        raise AssertionError("No se rechazó el archivo demasiado grande")

    print("\nTodas las pruebas fueron exitosas")



