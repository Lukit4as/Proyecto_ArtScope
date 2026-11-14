from pydantic import BaseModel
from pydantic import Field


class ImageInfoResponse(BaseModel):
    """Información técnica de una imagen."""

    width: int
    height: int
    format: str | None
    mode: str
    shape: list[int]
    dtype: str
    channels: int
    memory_bytes: int


class StoredImageResponse(BaseModel):
    """Información de una imagen alamcenada."""

    file_name: str
    url: str
    size_bytes: int


class ErrorResponse(BaseModel):
    """Estructura uniforme para comunicar errores."""

    detail: str

class ImageUploadResponse(BaseModel):
    """Respuesta de una carga de imagen."""

    stored_image: StoredImageResponse
    image_info: ImageInfoResponse



class OperationRequest(BaseModel):
    """Datos necesarios para ejecutar una operación."""

    operation: str
    parameters: dict = Field(default_factory=dict)


class GrayscaleAnalysisResponse(BaseModel):
    histogram : list[int]
    minimum: int
    maximum: int
    mean: float


class ColorHistogramResponses(BaseModel):
    blue: list[int]
    green: list[int]
    red: list[int]


class ImageAnalysisResponse(BaseModel):
    color_histograms: ColorHistogramResponses
    grayscale: GrayscaleAnalysisResponse