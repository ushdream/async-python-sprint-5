from fastapi import APIRouter
from .entity import router

api_router = APIRouter()
api_router.include_router(router, tags=["entities"])
