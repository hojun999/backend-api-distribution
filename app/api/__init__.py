from fastapi import APIRouter

from app.api.endpoints import buildings
from app.api.endpoints import navigation

router = APIRouter()
router.include_router(buildings.router, prefix="/api", tags=["buildings"])
router.include_router(navigation.router, prefix="/api/navigation", tags=["navigation"])
