from fastapi import APIRouter
from app.api.v1.endpoints import health, universe, assessment

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(assessment.router, tags=["Assessment & Recommendation"])
api_router.include_router(universe.router, tags=["Universe & Market Data"])

