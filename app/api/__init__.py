from fastapi import APIRouter

from app.api.endpoints import buildings

router = APIRouter()
router.include_router(buildings.router, prefix="/api", tags=["buildings"])
