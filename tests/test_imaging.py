from app.core.imaging import (
  load_image,
  get_image_info,
  get_pixel
 )

# 1. Cargar la imagen
image = load_image("examples/pintura1.jpg")

# 2. Obtener información técnica
info = get_image_info(image)


print("INFORMACIÓN DE LA IMAGEN")
for key, value in info.items():
    print(f"{key}: {value}")

# 3. Consultar un píxel
pixel = get_pixel(image, 0, 0)

print("\nVALOR DEL PRIMER PÍXEL:")
print(pixel)


