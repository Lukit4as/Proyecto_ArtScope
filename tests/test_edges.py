import cv2

from app.core.imaging import(
    load_image_cv2,
    convert_to_grayscale
)

from app.core.analysis import detect_edges

# 1. Cargar imagen
image = load_image_cv2("examples/pintura1.jpg")

# 2. Convertir a escala de grises
grayscale_image = convert_to_grayscale(image)


# 3. Detectar bordes con los valores predeterminados
edges = detect_edges(grayscale_image)

# 4. Comparar diferentes configuraciones
edges_1 = detect_edges(grayscale_image, 50, 100)
edges_2 = detect_edges(grayscale_image, 100, 200)
edges_3 = detect_edges(grayscale_image, 150, 250)

# 5. Guardar resultados
cv2.imwrite("outputs/pintura_edges.png", edges)
cv2.imwrite("outputs/edges_50_100.png", edges_1)
cv2.imwrite("outputs/edges_100_200.png", edges_2)
cv2.imwrite("outputs/edges_150_250.png", edges_3)

print("Detección de bordes y comparación completadas.")

print("\nCOMPARACIÓN DE BORDES")

print("50-100:", cv2.countNonZero(edges_1))
print("100-200:", cv2.countNonZero(edges_2))
print("150-250:", cv2.countNonZero(edges_3))