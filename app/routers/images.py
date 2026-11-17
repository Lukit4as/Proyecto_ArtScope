
"""
images.py

Endpoints para carga, análisis, detección de bordes
y restauración de imágenes en ArtScope.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app import schemas

from app.services.image_service import (
    upload_image,
    analyze_stored_image,
    detect_stored_image_edges,
    restore_stored_image
)

router = APIRouter()


# ========================================
# CARGA DE IMÁGENES
# ========================================

@router.post(
    "/images",
    response_model=schemas.ImageUploadResponse
)
async def upload_image_endpoint(
    file: UploadFile = File(...)
):
    """
    Recibe una imagen, la valida y la almacena.
    """

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

    finally:

        await file.close()


# ========================================
# ANÁLISIS DE IMÁGENES
# ========================================

@router.get(
    "/images/{file_name}/analysis"
)
def analyze_image_endpoint(
    file_name: str
):
    """
    Devuelve histogramas RGB y estadísticas
    de luminosidad de una imagen almacenada.
    """

    try:

        return analyze_stored_image(file_name)

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


# ========================================
# DETECCIÓN DE BORDES
# ========================================

@router.post(
    "/images/{file_name}/edges",
    response_model=schemas.StoredImageResponse
)
def detect_edges_endpoint(
    file_name: str,
    threshold1: int = 100,
    threshold2: int = 200
):
    """
    Detecta los bordes mediante el algoritmo Canny.
    """

    try:

        return detect_stored_image_edges(
            file_name,
            threshold1,
            threshold2
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


# ========================================
# RESTAURACIÓN DE IMÁGENES
# ========================================

@router.post(
    "/images/{file_name}/restore",
    response_model=schemas.StoredImageResponse
)
def restore_image_endpoint(
    file_name: str,
    request: schemas.OperationRequest
):
    """
    Aplica una técnica de restauración a una imagen.

    Técnicas disponibles:
    - denoise
    - color-correction
    - detail-enhancement
    - inpainting
    """

    try:

        return restore_stored_image(
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
