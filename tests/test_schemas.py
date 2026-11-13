from pydantic import ValidationError

from app.schemas import(
    ImageInfoResponse,
    StoredImageResponse,
    ErrorResponse
)

print("PRUEBA DE SCHEMAS")

# 1. Información técnica
image_info = ImageInfoResponse(
    width=429,
    height=640,
    format="JPEG",
    mode="RGB",
    shape=[640, 429, 3],
    dtype="uint8",
    channels=3,
    memory_bytes=823680
)

print("Información de imagen:", image_info.model_dump())


# 2. Imagen almacenada
stored_image = StoredImageResponse(
    file_name="pintura.jpeg",
    url="/media/pintura.jpeg",
    size_bytes=95872
)

print("Imagen almacenada:", stored_image.model_dump())


# 3. Error
error = ErrorResponse(
    detail="No se pudo procesar la imagen."
)

print("Error:", error.model_dump())


# 4. Validación de datos incorrectos
try:
    ImageInfoResponse(
        width="ancho",
        height=640,
        format="JPEG",
        mode="RGB",
        shape=[640, 429, 3],
        dtype="uint8",
        channels=3,
        memory_bytes=823680
    )

except ValidationError:
      print("Validación de datos incorrectos: correcta")


print("\nTodas las pruebas fueron exitosas.")