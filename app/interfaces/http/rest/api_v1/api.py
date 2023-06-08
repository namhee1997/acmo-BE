from fastapi import APIRouter
from app.interfaces.http.rest.api_v1.endpoints import auth


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
