
import numpy as np

from app.core.imaging import (
    load_image_cv2,
    convert_bgr_to_rgb,
    load_image
)

image_path = "examples/pintura1.jpg"

# 1. Cargar la imagen con OpenCV
image_bgr = load_image_cv2(image_path)

# 2. Convertir la imagen a RGB
image_rgb = convert_bgr_to_rgb(image_bgr)

# 3. Cargar la imagen con Pillow
pil_image = load_image(image_path)
pil_array = np.asarray(pil_image)

# 4. Mostrar resultados
print("IMAGEN CARGADA CON OPENCV")
print("Shape:", image_bgr.shape)

print("\nPRIMER PIXEL BGR:")
print(image_bgr[0, 0])

print("\nPRIMER PIXEL RGB:")
print(image_rgb[0, 0])

print("\nPRIMER PIXEL PILLOW:")
print(pil_array[0, 0])

# 5. Comparar las imágenes completas
print("\n¿COINCIDEN LAS IMÁGENES?")
print(np.array_equal(image_rgb, pil_array))
