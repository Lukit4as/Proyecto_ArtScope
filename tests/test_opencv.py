import cv2
import numpy as np
from PIL import Image

#Ruta de nuestra imagen
image_path = "examples/pintura1.jpg"

# 1. Cargar la imagen con OpenCV
opencv_image = cv2.imread(image_path)

# 2. Verificar que la imagen se haya cargado
if opencv_image is None:
    raise FileNotFoundError( 
        f"No se pudo cargar la imagen: {image_path}"
    )

# 3. Obtener información de la imagen
print("INFORMACIÓN CON OPENCV")
print("Shape:", opencv_image.shape)
print("Dtype:", opencv_image.dtype)
print("Canales:", opencv_image.shape[2])

# 4. Consultar el primer píxel
opencv_pixel = opencv_image[0, 0]

print("\nPRIMER PÍXEL CON OPENCV (BGR):")
print(opencv_pixel)

# 5. Cargar la misma imagen con Pillow
pil_image = Image.open(image_path)
pil_array = np.asarray(pil_image)

pil_pixel = pil_array[0, 0]

print ("\nPRIMER PÍXEL CON PILLOW (RGB):")
print(pil_pixel)

# 6. Comparar los valores
print ("\nCOMPARACIÓN")
print("OpenCV BGR:", opencv_pixel)
print("Pillow RGB:", pil_pixel)

# 7. Convertir la imagen de BGR a RGB
rgb_image = cv2.cvtColor(
    opencv_image,
    cv2.COLOR_BGR2RGB
)

#8. Consultar el primer píxel convertido
rgb_pixel = rgb_image[0, 0]
print ("\nPRIMER PÍXEL DESPUES DE LA CONVERSIÓN")
print(rgb_pixel)

# 9. Comprobar que coincide con Pillow
print("\n¿COINCIDEN LOS PÍXELES?")
print(np.array_equal(rgb_pixel, pil_pixel))
