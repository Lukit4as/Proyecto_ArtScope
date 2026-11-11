import matplotlib.pyplot as plt
from app.core.imaging import (
    load_image_cv2,
    convert_to_grayscale
)

from app.core.analysis import calculate_grayscale_histogram

# 1. Cargar la pintura
image = load_image_cv2("examples/pintura1.jpg")

# 2. Convertir a escala de grises
grayscale_image = convert_to_grayscale(image)

# 3. Calcular histograma y estadísticas
results = calculate_grayscale_histogram(grayscale_image)

# 4. Mostrar resultados
print("ANÁLISIS DE LUMINOSIDAD")

print("Intensidad mínima:", results["minimum"])
print("Intensidad máxima:", results["maximum"])
print("Intensidad promedio:", results["mean"])

print("Cantidad de valores:", len(results["histogram"]))
print("Total de píxeles:", int(results["histogram"].sum()))

plt.figure(figsize=(10, 5))

plt.plot(results["histogram"], color="gray")

plt.title("Histograma de luminosidad - ArtScope")
plt.xlabel("Intensidad (0-255)")
plt.ylabel("Cantidad de píxeles")

plt.xlim(0, 255)
plt.grid(alpha=0.3)

plt.savefig(
    "outputs/histograma_luminosidad.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("Gráfico guardado correctamente.")
