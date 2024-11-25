from fastapi import APIRouter, HTTPException
from typing import Dict

health_router = APIRouter()


@health_router.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


@health_router.get("/readiness")
async def readiness_check() -> Dict[str, str]:
    # Add database connection check
    # Add Redis connection check
    return {"status": "ready"}
