"""
API v1 라우터
"""

from fastapi import APIRouter
from app.api.v1.routes import generation, services, health, models

api_router = APIRouter()

# 라우터 등록
api_router.include_router(generation.router, prefix="/generate", tags=["generation"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(models.router, prefix="/models", tags=["models"])

