from fastapi import APIRouter

# from app.api.endpoints import items
from app.api.endpoints import picking
from app.api.endpoints import carrier_selection

api_router = APIRouter()
# api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(picking.router, prefix="/pickings", tags=["pickings"])
api_router.include_router(carrier_selection.router, prefix="/carrier-selection", tags=["carrier-selection"]) 