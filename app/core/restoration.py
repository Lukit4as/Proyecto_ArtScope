
"""
restoration.py

Funciones de restauración digital de pinturas para ArtScope.

El objetivo es mejorar la apariencia visual de una obra
preservando sus colores, bordes, pinceladas y texturas.

Incluye técnicas tradicionales de OpenCV y reconstrucción
mediante inteligencia artificial con el modelo LaMa.
"""

import importlib.util
import threading
from pathlib import Path

import cv2
import numpy as np


# ========================================
# CONFIGURACIÓN DEL MODELO LAMA
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LAMA_DIRECTORY = PROJECT_ROOT / "models" / "inpainting_lama"
LAMA_MODEL_PATH = LAMA_DIRECTORY / "inpainting_lama_2025jan.onnx"
LAMA_MODULE_PATH = LAMA_DIRECTORY / "lama.py"

_lama_model = None
_lama_lock = threading.Lock()

MASK_FEATHER_SIZE = 15


def validate_image(image: np.ndarray) -> None:
    """Valida que la imagen sea un array NumPy BGR uint8."""

    if not isinstance(image, np.ndarray):
        raise TypeError("La imagen debe ser un array de NumPy.")

    if image.dtype != np.uint8:
        raise ValueError("La imagen debe tener valores uint8.")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("La imagen debe tener tres canales BGR.")


def _load_lama_model():
    """Carga LaMa de forma diferida y conserva la instancia."""

    global _lama_model

    if _lama_model is not None:
        return _lama_model

    if not LAMA_MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"No se encontró el modelo LaMa: {LAMA_MODEL_PATH}"
        )

    if not LAMA_MODULE_PATH.is_file():
        raise FileNotFoundError(
            f"No se encontró el módulo LaMa: {LAMA_MODULE_PATH}"
        )

    try:
        spec = importlib.util.spec_from_file_location(
            "artscope_lama_model",
            LAMA_MODULE_PATH
        )

        if spec is None or spec.loader is None:
            raise ImportError(
                "No se pudo preparar la carga del módulo lama.py."
            )

        lama_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lama_module)

        _lama_model = lama_module.Lama(
            modelPath=str(LAMA_MODEL_PATH)
        )

    except Exception as error:
        _lama_model = None

        raise RuntimeError(
            "No se pudo cargar el modelo de inteligencia artificial LaMa."
        ) from error

    return _lama_model


# ========================================
# REDUCCIÓN DE RUIDO
# ========================================

def reduce_noise(
    image: np.ndarray,
    diameter: int = 7,
    sigma_color: float = 35,
    sigma_space: float = 35
) -> np.ndarray:
    """Reduce el ruido mediante un filtro bilateral."""

    validate_image(image)

    if diameter <= 0:
        raise ValueError("El diámetro debe ser positivo.")

    if sigma_color <= 0 or sigma_space <= 0:
        raise ValueError("Los parámetros sigma deben ser positivos.")

    return cv2.bilateralFilter(
        image,
        diameter,
        sigma_color,
        sigma_space
    )


# ========================================
# CORRECCIÓN DE COLOR
# ========================================

def correct_color(
    image: np.ndarray,
    clip_limit: float = 1.5,
    tile_grid_size: int = 8
) -> np.ndarray:
    """Mejora el contraste local utilizando LAB y CLAHE."""

    validate_image(image)

    if clip_limit <= 0:
        raise ValueError("El límite de contraste debe ser positivo.")

    if tile_grid_size <= 0:
        raise ValueError("El tamaño de la cuadrícula debe ser positivo.")

    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    lightness, channel_a, channel_b = cv2.split(lab_image)

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(tile_grid_size, tile_grid_size)
    )

    corrected_lightness = clahe.apply(lightness)

    corrected_lab = cv2.merge(
        (corrected_lightness, channel_a, channel_b)
    )

    return cv2.cvtColor(
        corrected_lab,
        cv2.COLOR_LAB2BGR
    )


# ========================================
# MEJORA DE DETALLES
# ========================================

def enhance_details(
    image: np.ndarray,
    strength: float = 0.35,
    sigma: float = 1.0
) -> np.ndarray:
    """Realza detalles mediante una máscara de enfoque suave."""

    validate_image(image)

    if not 0 <= strength <= 1:
        raise ValueError("La intensidad debe estar entre 0 y 1.")

    if sigma <= 0:
        raise ValueError("Sigma debe ser positivo.")

    blurred = cv2.GaussianBlur(
        image,
        (0, 0),
        sigma
    )

    return cv2.addWeighted(
        image,
        1.0 + strength,
        blurred,
        -strength,
        0
    )


# ========================================
# INPAINTING TRADICIONAL CON OPENCV
# ========================================

def reconstruct_damage(
    image: np.ndarray,
    mask: np.ndarray,
    radius: float = 3.0,
    method: str = "telea"
) -> np.ndarray:
    """Reconstruye regiones seleccionadas mediante inpainting."""

    validate_image(image)

    if not isinstance(mask, np.ndarray):
        raise TypeError("La máscara debe ser un array de NumPy.")

    if mask.ndim != 2:
        raise ValueError("La máscara debe ser de un solo canal.")

    if mask.shape != image.shape[:2]:
        raise ValueError(
            "La máscara debe tener las dimensiones de la imagen."
        )

    if radius <= 0:
        raise ValueError("El radio debe ser positivo.")

    methods = {
        "telea": cv2.INPAINT_TELEA,
        "ns": cv2.INPAINT_NS
    }

    if method not in methods:
        raise ValueError("Método de reconstrucción no disponible.")

    return cv2.inpaint(
        image,
        mask.astype(np.uint8),
        radius,
        methods[method]
    )


# ========================================
# COMPOSICIÓN CON MÁSCARA SUAVIZADA
# ========================================

def _blend_restoration(
    original: np.ndarray,
    reconstructed: np.ndarray,
    mask: np.ndarray
) -> np.ndarray:
    """Combina la imagen original con la reconstrucción de LaMa."""

    if MASK_FEATHER_SIZE <= 0 or MASK_FEATHER_SIZE % 2 == 0:
        raise ValueError(
            "MASK_FEATHER_SIZE debe ser un número impar positivo."
        )

    feathered_mask = cv2.GaussianBlur(
        mask,
        (MASK_FEATHER_SIZE, MASK_FEATHER_SIZE),
        0
    )

    alpha = feathered_mask.astype(np.float32) / 255.0
    alpha = alpha[:, :, np.newaxis]

    blended = (
        original.astype(np.float32) * (1.0 - alpha)
        + reconstructed.astype(np.float32) * alpha
    )

    return np.clip(blended, 0, 255).astype(np.uint8)


# ========================================
# INPAINTING CON INTELIGENCIA ARTIFICIAL
# ========================================

def reconstruct_damage_lama(
    image: np.ndarray,
    mask: np.ndarray
) -> np.ndarray:
    """Reconstruye regiones seleccionadas utilizando LaMa."""

    validate_image(image)

    if not isinstance(mask, np.ndarray):
        raise TypeError("La máscara debe ser un array de NumPy.")

    if mask.ndim != 2:
        raise ValueError("La máscara debe ser de un solo canal.")

    if mask.shape != image.shape[:2]:
        raise ValueError(
            "La máscara debe tener las dimensiones de la imagen."
        )

    binary_mask = np.where(
        mask > 0,
        255,
        0
    ).astype(np.uint8)

    if not np.any(binary_mask):
        raise ValueError(
            "La máscara no contiene ninguna zona seleccionada."
        )

    selected_pixels = cv2.countNonZero(binary_mask)
    total_pixels = binary_mask.size

    selected_percentage = (
        selected_pixels / total_pixels
    ) * 100

    ys, xs = np.where(binary_mask > 0)

    print("\n========== DIAGNÓSTICO LAMA ==========")
    print("Imagen original:", image.shape)
    print("Máscara:", binary_mask.shape)
    print("Píxeles seleccionados:", selected_pixels)
    print(
        "Porcentaje seleccionado:",
        round(selected_percentage, 2),
        "%"
    )

    print(
        "Región seleccionada (x, y, ancho, alto):",
        (
            int(xs.min()),
            int(ys.min()),
            int(xs.max() - xs.min() + 1),
            int(ys.max() - ys.min() + 1)
        )
    )

    model = _load_lama_model()

    try:
        with _lama_lock:
            reconstructed = model.infer(
                image,
                binary_mask
            )

    except Exception as error:
        raise RuntimeError(
            "Ocurrió un error durante la reconstrucción con LaMa."
        ) from error

    if not isinstance(reconstructed, np.ndarray):
        raise RuntimeError(
            "LaMa no devolvió una imagen válida."
        )

    if reconstructed.ndim != 3 or reconstructed.shape[2] != 3:
        raise RuntimeError(
            "El resultado de LaMa no tiene tres canales de color."
        )

    if reconstructed.shape[:2] != image.shape[:2]:
        reconstructed = cv2.resize(
            reconstructed,
            (image.shape[1], image.shape[0]),
            interpolation=cv2.INTER_LINEAR
        )

    reconstructed = np.clip(
        reconstructed,
        0,
        255
    ).astype(np.uint8)

    raw_difference = cv2.absdiff(
        image,
        reconstructed
    )

    raw_difference_gray = cv2.cvtColor(
        raw_difference,
        cv2.COLOR_BGR2GRAY
    )

    inside_mask = raw_difference_gray[binary_mask > 0]
    outside_mask = raw_difference_gray[binary_mask == 0]

    print("\n========== RESULTADO ORIGINAL DE LAMA ==========")
    print("Dimensiones devueltas:", reconstructed.shape)

    print(
        "Diferencia media general:",
        round(float(np.mean(raw_difference_gray)), 2)
    )

    if inside_mask.size > 0:
        print(
            "Diferencia media dentro de la máscara:",
            round(float(np.mean(inside_mask)), 2)
        )

        print(
            "Píxeles modificados dentro de la máscara (>10):",
            round(float(np.mean(inside_mask > 10) * 100), 2),
            "%"
        )

    if outside_mask.size > 0:
        print(
            "Diferencia media fuera de la máscara:",
            round(float(np.mean(outside_mask)), 2)
        )

    restored_image = _blend_restoration(
        image,
        reconstructed,
        binary_mask
    )

    final_difference = cv2.absdiff(
        image,
        restored_image
    )

    final_difference_gray = cv2.cvtColor(
        final_difference,
        cv2.COLOR_BGR2GRAY
    )

    final_inside_mask = final_difference_gray[binary_mask > 0]
    final_outside_mask = final_difference_gray[binary_mask == 0]

    print("\n========== RESULTADO COMBINADO ==========")

    print(
        "Diferencia media general:",
        round(float(np.mean(final_difference_gray)), 2)
    )

    if final_inside_mask.size > 0:
        print(
            "Diferencia media dentro de la máscara:",
            round(float(np.mean(final_inside_mask)), 2)
        )

    if final_outside_mask.size > 0:
        print(
            "Diferencia media fuera de la máscara:",
            round(float(np.mean(final_outside_mask)), 2)
        )

    print("=========================================\n")

    return restored_image


# ========================================
# RESTAURACIÓN COMBINADA
# ========================================

def restore_combined(
    image: np.ndarray,
    operations: dict
) -> np.ndarray:
    """Aplica varias técnicas de restauración sobre una imagen."""

    validate_image(image)

    if not isinstance(operations, dict):
        raise TypeError("Las operaciones deben enviarse como un diccionario.")

    operation_order = (
        "denoise",
        "color_correction",
        "detail_enhancement"
    )

    unknown_operations = set(operations.keys()) - set(operation_order)

    if unknown_operations:
        raise ValueError(
            "Se recibieron operaciones no reconocidas: "
            + ", ".join(sorted(unknown_operations))
        )

    restored = image.copy()

    for operation_name in operation_order:
        config = operations.get(operation_name, {})

        if not isinstance(config, dict):
            raise ValueError(
                f"La configuración de '{operation_name}' debe ser un objeto."
            )

        enabled = config.get("enabled", False)
        intensity = config.get("intensity", 0)

        if not isinstance(enabled, bool):
            raise ValueError(
                f"'enabled' de '{operation_name}' debe ser verdadero o falso."
            )

        if isinstance(intensity, bool) or not isinstance(intensity, (int, float)):
            raise ValueError(
                f"La intensidad de '{operation_name}' debe ser numérica."
            )

        if not 0 <= intensity <= 100:
            raise ValueError(
                f"La intensidad de '{operation_name}' debe estar entre 0 y 100."
            )

        if not enabled or intensity == 0:
            continue

        intensity = float(intensity) / 100.0

        if operation_name == "denoise":
            diameter = 3 + 2 * round(intensity * 3)
            sigma_color = 15 + intensity * 85
            sigma_space = 15 + intensity * 85

            restored = reduce_noise(
                restored,
                diameter=diameter,
                sigma_color=sigma_color,
                sigma_space=sigma_space
            )

        elif operation_name == "color_correction":
            corrected = correct_color(
                restored,
                clip_limit=1.0 + intensity * 2.0,
                tile_grid_size=8
            )

            restored = cv2.addWeighted(
                restored,
                1.0 - intensity,
                corrected,
                intensity,
                0
            )

        elif operation_name == "detail_enhancement":
            restored = enhance_details(
                restored,
                strength=intensity * 0.8,
                sigma=1.0
            )

    return restored


# ========================================
# RESTAURACIÓN AUTOMÁTICA GLOBAL
# ========================================

def restore_automatic(
    image: np.ndarray,
    denoise_strength: float = 0.5,
    color_strength: float = 0.5,
    detail_strength: float = 0.25
) -> np.ndarray:
    """
    Aplica una mejora automática y conservadora a toda la pintura.

    Las intensidades aceptan valores entre 0 y 1. El procesamiento
    estima el nivel de ruido y el contraste de la imagen para moderar
    las operaciones.

    No utiliza máscaras ni reconstruye contenido pictórico
    desaparecido. Para eso se necesita un modelo generativo
    especializado o una selección de regiones para inpainting.
    """

    validate_image(image)

    strengths = {
        "denoise_strength": denoise_strength,
        "color_strength": color_strength,
        "detail_strength": detail_strength
    }

    for name, value in strengths.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(
                f"{name} debe ser un número entre 0 y 1."
            )

        if not 0 <= value <= 1:
            raise ValueError(
                f"{name} debe estar entre 0 y 1."
            )

    restored = image.copy()

    gray = cv2.cvtColor(
        restored,
        cv2.COLOR_BGR2GRAY
    )

    # Estimación aproximada del ruido.
    median = cv2.medianBlur(gray, 3)
    high_frequency = cv2.absdiff(gray, median)
    noise_estimate = float(np.median(high_frequency))

    # Ajustar la reducción de ruido según la estimación.
    adaptive_denoise = float(denoise_strength) * min(
        1.0,
        noise_estimate / 12.0
    )

    if adaptive_denoise > 0.03:
        diameter = 3 if adaptive_denoise < 0.35 else 5

        sigma_color = 12.0 + adaptive_denoise * 38.0
        sigma_space = 12.0 + adaptive_denoise * 38.0

        denoised = reduce_noise(
            restored,
            diameter=diameter,
            sigma_color=sigma_color,
            sigma_space=sigma_space
        )

        restored = cv2.addWeighted(
            restored,
            1.0 - adaptive_denoise,
            denoised,
            adaptive_denoise,
            0
        )

    # Evaluar el rango tonal.
    gray = cv2.cvtColor(
        restored,
        cv2.COLOR_BGR2GRAY
    )

    low, high = np.percentile(
        gray,
        (5, 95)
    )

    tonal_range = float(high - low)

    contrast_deficit = max(
        0.0,
        min(1.0, (150.0 - tonal_range) / 100.0)
    )

    adaptive_color = float(color_strength) * contrast_deficit

    if adaptive_color > 0.02:
        corrected = correct_color(
            restored,
            clip_limit=1.0 + adaptive_color * 1.5,
            tile_grid_size=8
        )

        restored = cv2.addWeighted(
            restored,
            1.0 - adaptive_color,
            corrected,
            adaptive_color,
            0
        )

    # Mejora moderada de detalles.
    effective_detail = float(detail_strength) * 0.6

    if effective_detail > 0:
        restored = enhance_details(
            restored,
            strength=effective_detail,
            sigma=1.0
        )

    return np.clip(
        restored,
        0,
        255
    ).astype(np.uint8)



# ========================================
# DETECCIÓN EXPERIMENTAL AUTOMÁTICA DE DAÑOS
# ========================================

def detect_damage_mask(
    image: np.ndarray,
    sensitivity: int = 55,
    max_damage_percent: float = 6.0
) -> np.ndarray:
    """
    Genera una máscara experimental de anomalías finas oscuras o claras.

    Puede detectar grietas y rayones, pero también confundirlos
    con pinceladas, bordes y texturas originales.
    """

    validate_image(image)

    if (
        isinstance(sensitivity, bool)
        or not isinstance(sensitivity, int)
        or not 1 <= sensitivity <= 100
    ):
        raise ValueError(
            "La sensibilidad debe ser un entero entre 1 y 100."
        )

    if not 0.5 <= max_damage_percent <= 10.0:
        raise ValueError(
            "El porcentaje máximo debe estar entre 0.5 y 10."
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    local = cv2.medianBlur(gray, 9)

    dark_residual = cv2.subtract(local, gray)
    bright_residual = cv2.subtract(gray, local)

    threshold = int(30 - (sensitivity - 1) * 0.18)
    threshold = max(12, min(30, threshold))

    anomalies = cv2.max(dark_residual, bright_residual)

    _, mask = cv2.threshold(
        anomalies,
        threshold,
        255,
        cv2.THRESH_BINARY
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    )

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask,
        8
    )

    filtered = np.zeros_like(mask)

    min_area = max(
        4,
        int(image.shape[0] * image.shape[1] * 0.000002)
    )

    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])

        if area >= min_area and max(width, height) >= 3:
            filtered[labels == label] = 255

    max_pixels = int(filtered.size * max_damage_percent / 100.0)

    if cv2.countNonZero(filtered) > max_pixels:
        for stricter in (threshold + 8, threshold + 16, threshold + 24):
            _, candidate = cv2.threshold(
                anomalies,
                min(250, stricter),
                255,
                cv2.THRESH_BINARY
            )

            candidate = cv2.morphologyEx(
                candidate,
                cv2.MORPH_OPEN,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            )

            if cv2.countNonZero(candidate) <= max_pixels:
                filtered = candidate
                break
        else:
            return np.zeros_like(gray)

    if cv2.countNonZero(filtered) == 0:
        return filtered

    filtered = cv2.dilate(
        filtered,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
        iterations=1
    )

    final_percent = (
        cv2.countNonZero(filtered) / filtered.size
    ) * 100.0

    if final_percent > max_damage_percent:
        return np.zeros_like(gray)

    return filtered
