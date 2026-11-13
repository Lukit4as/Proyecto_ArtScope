from fastapi import APIRouter, UploadFile, File, HTTPException

from app import schemas
from app.services.image_service import upload_image

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

    