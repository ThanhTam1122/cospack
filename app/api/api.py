from fastapi import APIRouter
from app.api.endpoints import picking

api_router = APIRouter()
api_router.include_router(picking.router, prefix="/pickings", tags=["pickings"]) 