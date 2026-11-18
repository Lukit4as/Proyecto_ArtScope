
import cv2 as cv
import numpy as np


# Reducir memoria auxiliar utilizada por OpenCV.
cv.setNumThreads(1)
cv.ocl.setUseOpenCL(False)


class Lama:
    INPUT_SIZE = 512

    def __init__(
        self,
        modelPath="inpainting_lama_2025jan.onnx",
        backendId=cv.dnn.DNN_BACKEND_OPENCV,
        targetId=cv.dnn.DNN_TARGET_CPU
    ):
        self._modelPath = modelPath
        self._backendId = backendId
        self._targetId = targetId

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
        Ejecuta LaMa con entrada de 512x512,
        conservando las proporciones de la imagen.
        """

        if (
            not isinstance(image, np.ndarray)
            or image.ndim != 3
            or image.shape[2] != 3
            or image.dtype != np.uint8
        ):
            raise ValueError(
                "La imagen debe ser un array BGR uint8 de tres canales."
            )

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

        # 1. Redimensionamiento proporcional.
        scale = min(
            self.INPUT_SIZE / original_width,
            self.INPUT_SIZE / original_height
        )

        resized_width = max(1, int(round(original_width * scale)))
        resized_height = max(1, int(round(original_height * scale)))

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

        # 2. Calcular padding.
        horizontal_padding = self.INPUT_SIZE - resized_width
        vertical_padding = self.INPUT_SIZE - resized_height

        left = horizontal_padding // 2
        right = horizontal_padding - left
        top = vertical_padding // 2
        bottom = vertical_padding - top

        # 3. Aplicar padding.
        padded_image = cv.copyMakeBorder(
            resized_image,
            top,
            bottom,
            left,
            right,
            cv.BORDER_REFLECT_101
        )

        padded_mask = cv.copyMakeBorder(
            resized_mask,
            top,
            bottom,
            left,
            right,
            cv.BORDER_CONSTANT,
            value=0
        )

        # Liberar las imágenes intermedias que ya no se necesitan.
        del resized_image
        del resized_mask

        # 4. Preparar entradas del modelo.
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

        # Convertir la máscara a valores binarios sin crear
        # un segundo array temporal.
        np.greater(mask_blob, 0, out=mask_blob)

        del padded_image
        del padded_mask

        # 5. Inferencia.
        self._model.setInput(image_blob, "image")
        self._model.setInput(mask_blob, "mask")

        # Las entradas ya fueron transferidas al objeto Net.
        del image_blob
        del mask_blob

        output = self._model.forward()

        if (
            output.ndim != 4
            or output.shape[0] != 1
            or output.shape[1] != 3
        ):
            raise RuntimeError(
                f"Formato de salida LaMa inesperado: {output.shape}"
            )

        # 6. Convertir salida.
        result = output[0].transpose(1, 2, 0)
        result = np.clip(result, 0, 255).astype(np.uint8)

        del output

        # 7. Eliminar padding.
        result = result[
            top:top + resized_height,
            left:left + resized_width
        ]

        # 8. Recuperar dimensiones originales.
        if (
            result.shape[1] != original_width
            or result.shape[0] != original_height
        ):
            result = cv.resize(
                result,
                (original_width, original_height),
                interpolation=cv.INTER_CUBIC
            )

        return result
