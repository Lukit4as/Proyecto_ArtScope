
import cv2 as cv
import numpy as np


class Lama:
    INPUT_SIZE = 512

    def __init__(
        self,
        modelPath="inpainting_lama_2025jan.onnx",
        backendId=0,
        targetId=0
    ):
        self._modelPath = modelPath
        self._backendId = backendId
        self._targetId = targetId

        # Cargar el modelo ONNX.
        self._model = cv.dnn.readNetFromONNX(self._modelPath)

        self.setBackendAndTarget(
            self._backendId,
            self._targetId
        )

    @property
    def name(self):
        return self.__class__.__name__

    def setBackendAndTarget(self, backendId, targetId):
        self._backendId = backendId
        self._targetId = targetId

        self._model.setPreferableBackend(self._backendId)
        self._model.setPreferableTarget(self._targetId)

    def infer(self, image, mask):
        """
        Ejecuta la reconstrucción con LaMa conservando
        las proporciones originales de la imagen.

        La imagen se adapta a 512x512 mediante padding.
        La máscara utiliza exactamente la misma transformación.
        """

        # Validar imagen.
        if (
            not isinstance(image, np.ndarray)
            or image.ndim != 3
            or image.shape[2] != 3
            or image.dtype != np.uint8
        ):
            raise ValueError(
                "La imagen debe ser un array BGR uint8 de tres canales."
            )

        # Validar máscara.
        if (
            not isinstance(mask, np.ndarray)
            or mask.ndim != 2
            or mask.shape != image.shape[:2]
        ):
            raise ValueError(
                "La máscara debe tener las mismas dimensiones "
                "que la imagen y un solo canal."
            )

        original_height, original_width = image.shape[:2]

        # ========================================
        # 1. REDIMENSIONAMIENTO PROPORCIONAL
        # ========================================

        scale = min(
            self.INPUT_SIZE / original_width,
            self.INPUT_SIZE / original_height
        )

        resized_width = max(
            1,
            int(round(original_width * scale))
        )

        resized_height = max(
            1,
            int(round(original_height * scale))
        )

        resized_image = cv.resize(
            image,
            (resized_width, resized_height),
            interpolation=cv.INTER_AREA
        )

        resized_mask = cv.resize(
            mask,
            (resized_width, resized_height),
            interpolation=cv.INTER_NEAREST
        )

        # ========================================
        # 2. CALCULAR EL PADDING
        # ========================================

        horizontal_padding = self.INPUT_SIZE - resized_width
        vertical_padding = self.INPUT_SIZE - resized_height

        left = horizontal_padding // 2
        right = horizontal_padding - left

        top = vertical_padding // 2
        bottom = vertical_padding - top

        # ========================================
        # 3. APLICAR PADDING
        # ========================================

        # Reflejar los bordes de la pintura evita
        # introducir franjas negras artificiales.
        padded_image = cv.copyMakeBorder(
            resized_image,
            top,
            bottom,
            left,
            right,
            cv.BORDER_REFLECT_101
        )

        # El padding de la máscara debe quedar en cero:
        # esas zonas no deben reconstruirse.
        padded_mask = cv.copyMakeBorder(
            resized_mask,
            top,
            bottom,
            left,
            right,
            cv.BORDER_CONSTANT,
            value=0
        )

        # ========================================
        # 4. PREPARAR LAS ENTRADAS DEL MODELO
        # ========================================

        image_blob = cv.dnn.blobFromImage(
            padded_image,
            1.0 / 255.0,
            (self.INPUT_SIZE, self.INPUT_SIZE),
            (0, 0, 0),
            False,
            False
        )

        mask_blob = cv.dnn.blobFromImage(
            padded_mask,
            scalefactor=1.0,
            size=(self.INPUT_SIZE, self.INPUT_SIZE),
            mean=(0,),
            swapRB=False,
            crop=False
        )

        mask_blob = (mask_blob > 0).astype(np.float32)

        # ========================================
        # 5. EJECUTAR LA INFERENCIA
        # ========================================

        self._model.setInput(image_blob, "image")
        self._model.setInput(mask_blob, "mask")

        output = self._model.forward()

        if (
            output.ndim != 4
            or output.shape[0] != 1
            or output.shape[1] != 3
        ):
            raise RuntimeError(
                f"Formato de salida LaMa inesperado: {output.shape}"
            )

        # ========================================
        # 6. CONVERTIR LA SALIDA A IMAGEN
        # ========================================

        result = output[0]
        result = np.transpose(result, (1, 2, 0))

        # El modelo devuelve valores en el rango 0-255.
        # No multiplicar nuevamente por 255.
        result = np.clip(
            result,
            0,
            255
        ).astype(np.uint8)

        # ========================================
        # 7. ELIMINAR EL PADDING
        # ========================================

        result = result[
            top:top + resized_height,
            left:left + resized_width
        ]

        # ========================================
        # 8. RECUPERAR LAS DIMENSIONES ORIGINALES
        # ========================================

        result = cv.resize(
            result,
            (original_width, original_height),
            interpolation=cv.INTER_CUBIC
        )

        return result
