from fastapi import FastAPI
from app.routers.health import router as health_router

app = FastAPI(
    title="ArtScope API",
    description="API para análisis y procesamiento de pinturas digitales",
    version="1.0.0"
)

app.include_router(health_router)