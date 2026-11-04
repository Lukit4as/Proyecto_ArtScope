import numpy as np

from app.core.imaging import (
    load_image_cv2,
    convert_to_grayscale
)

image_path = "examples/pintura1.jpg"

# 1. Cargar la imagen original
image_bgr = load_image_cv2(image_path)

# 2. Convertir a escala de grises
grayscale_image = convert_to_grayscale(image_bgr)

# 3. Mostrar información de la imagen original
print("IMAGEN ORIGINAL")
print("Shape:", image_bgr.shape)
print("Dtype:", image_bgr.dtype)

# 4. Mostrar información de la imagen en escala de grises
print("\nIMAGEN EN ESCALA DE GRISES")
print("Shape:", grayscale_image.shape)
print("Dtype:", grayscale_image.dtype)


# 5. Consultar el primer píxel
print("\nPRIMER PÍXEL EN ESCALA DE GRISES")
print(grayscale_image[0, 0])

# 6. Verificar la cantidad de dimensiones
print ("\n¿LA IMAGEN TIENE UN SOLO CANAL?")
print(grayscale_image.ndim == 2)

# 7. Guardar la imagen en escala de grises
import cv2

output_path = "outputs/pintura_grayscale.jpg"

cv2.imwrite(output_path, grayscale_image)

print("\nIMAGEN GUARDADA EN:")
print(output_path)


from PIL import Image

# 8. Cargar la imagen original con Pillow
pil_image = Image.open("examples/pintura1.jpg")

# 9. Convertila a escala de grises
pil_grayscale = pil_image.convert("L")

# 10. Convertir el resultado a una matriz NumPy
pil_gray_array = np.asarray(pil_grayscale)

# 11. Comparar los resultados
print("\nCOMPARACIÓN ENTRE OPENCV Y PILLOW")
print("Shape OpenCV:", grayscale_image.shape)
print("Shape Pillow:", pil_gray_array.shape)

print("\nPrimer píxel OpenCV:", grayscale_image[0, 0])
print("Primer píxel Pillow:", pil_gray_array[0, 0])

print("\n¿SON EXACTAMENTE IGUALES?")
print(np.array_equal(grayscale_image, pil_gray_array))

# 12. Guardar resultado de pillow
pil_grayscale.save("outputs/pintura_grayscale_pillow.png")
