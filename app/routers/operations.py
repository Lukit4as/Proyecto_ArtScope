from fastapi import APIRouter, HTTPException

from app.schemas import OperationRequest, StoredImageResponse
from app.services.image_service import process_stored_image

router = APIRouter(prefix="/images", tags=["Operations"])


@router.post(
    "/{file_name}/operations",
    response_model=StoredImageResponse
)
def process_image_endpoint(
    file_name: str,
    request: OperationRequest
):
    try:
        return process_stored_image(
            file_name,
            request.operation,
            request.parameters
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la imagen solicitada."
        ) from error

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error