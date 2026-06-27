from fastapi import APIRouter
from backend.app.api.v1.endpoints import router as query_endpoints_router
from backend.app.routes.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(query_endpoints_router, prefix="/api/v1")
api_router.include_router(upload_router, prefix="/api/v1")
