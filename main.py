from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="ArtScope API",
    description="API para análisis y procesamiento de pinturas digitales",
    version="1.0.0"
)

app.include_router(router)

