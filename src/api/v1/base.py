from fastapi import APIRouter
from .entity import router
from .api_auth import router_auth

api_router = APIRouter()
api_router.include_router(router_auth, tags=["auth"])
#api_router.include_router(router, tags=["entities"])


print(f'base is imported')
