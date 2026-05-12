from fastapi import APIRouter

from app.api.endpoints import buildings
from app.api.endpoints import navigation
from app.api.endpoints import processing

router = APIRouter()
router.include_router(buildings.router, prefix="/api", tags=["buildings"])
router.include_router(navigation.router, prefix="/api/navigation", tags=["navigation"])
router.include_router(processing.router, prefix="/api/processing", tags=["processing"])
