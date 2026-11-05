import matplotlib.pyplot as plt
from app.core.imaging import load_image_cv2
from app.core.analysis import calculate_color_histograms

image_path = "examples/pintura1.jpg"

# 1. Cargar la pintura
image = load_image_cv2(image_path)

# 2. Calcular los histogramas
histograms = calculate_color_histograms(image)

# 3. Mostrar información de cada canal
print("ANÁLISIS DE HISTOGRAMAS")

for channel_name, histogram in histograms.items():

    print(f"\nCANAL: {channel_name.upper()}")
    print("Cantidad de valores:", len(histogram))
    print("Total de píxeles:", int(histogram.sum()))
    print("Intensidad mas frecuente:", histogram.argmax())
    print("Frecuencia máxima:", int(histogram.max()))

# 4. Graficar los tres histogramas
plt.figure(figsize=(12, 6))

for channel_name,histogram in histograms.items():
    plt.plot(
        histogram,
        color=channel_name,
        label=channel_name.upper()
    )

plt.title("Distribución de colores - ArtScope")
plt.xlabel("Intensidad de color (0-255)")
plt.ylabel("Cantidad de píxeles")
plt.xlim(0, 255)
plt.legend()
plt.grid(alpha=0.3)

# 5. Guardar el gráfico
plt.savefig(
    "outputs/histogramas_color.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("\nGráfico guardado en outputs/histogramas_color.png")