from app.core import operations


def apply_image_operation(
        image,
        operation: str,
        parameters: dict | None = None
):
    if parameters is None:
        parameters = {}

    available_operations = {
        "brightness": operations.adjust_brightness,
        "contrast": operations.adjust_contrast,
        "blur": operations.apply_gaussian_blur,
        "sharpen": operations.apply_sharpen,
        "rotation": operations.rotate_image,
        "resize": operations.resize_image
    }

    if operation not in available_operations:
        raise ValueError(f"Operación no disponible: {operation}")

    selected_operation = available_operations[operation]

    return selected_operation(image, **parameters)
