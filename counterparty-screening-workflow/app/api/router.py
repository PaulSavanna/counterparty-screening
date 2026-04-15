from fastapi import APIRouter

from app.api.routes import checks, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(checks.router, tags=["checks"])
