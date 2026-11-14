from fastapi import APIRouter, UploadFile, File, HTTPException

from app import schemas
from app.services.image_service import upload_image
from app.schemas import ImageAnalysisResponse
from app.services.image_service import analyze_stored_image
from app.services.image_service import detect_stored_image_edges
from app.schemas import StoredImageResponse

router = APIRouter()


@router.post(
    "/images",
    response_model=schemas.ImageUploadResponse
)
async def upload_image_endpoint(
    file: UploadFile = File(...)
):
    try:
        image_bytes = await file.read()

        result = upload_image(image_bytes)

        return {
            "stored_image": result["stored_image"],
            "image_info": result["image_info"]
        }

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


@router.get(
    "/images/{file_name}/analysis"
)
def analyze_image_endpoint(file_name: str):
    """
    Analiza una imagen almacenada y devuelve sus histogramas y estadisticas de luminosidad.
    """

    try:
        return analyze_stored_image(file_name)

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la imagen solicitada"
        ) from error

@router.post("/images/{file_name}/edges", response_model=StoredImageResponse)
def detect_edges_endpoint(
    file_name:str,
    threshold1: int = 100,
    threshold2: int = 200
):
    try:
        return detect_stored_image_edges(
            file_name,
            threshold1,
            threshold2
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail = "No se encontró la imagen solicitada."
        ) from error

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            details=str(error)
        ) from error

