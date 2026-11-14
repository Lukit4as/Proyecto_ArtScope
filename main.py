from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app import config

from app.routers.health import router as health_router
from app.routers.images import router as images_router
from app.routers.operations import router as operations_router

app = FastAPI(
    title="ArtScope API",
    description="API para análisis y procesamiento de pinturas digitales",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(images_router)
app.include_router(operations_router)

config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/media",
    StaticFiles(directory=str(config.STORAGE_DIR)),
    name="media"
)