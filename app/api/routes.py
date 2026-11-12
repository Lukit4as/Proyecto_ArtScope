from fastapi import APIRouter, UploadFile, File, Form, HTTPException

router = APIRouter()

@router.get("/health")
def health_check():
    return{"status": "ok", "app": "ArtScope"}

import json
from io import BytesIO

import cv2
import numpy as np

from fastapi.responses import StreamingResponse
from app.services.image_service import apply_image_operation