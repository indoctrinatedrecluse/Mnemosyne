from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mnemosyne_api.api.routes.health import router as health_router
from mnemosyne_api.api.routes.worlds import router as worlds_router
from mnemosyne_api.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)
app.include_router(health_router)
app.include_router(worlds_router, prefix="/api/v1")
