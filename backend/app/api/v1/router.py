from fastapi import APIRouter
from app.api.v1.endpoints import health, universe

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(universe.router, tags=["Universe & Market Data"])

