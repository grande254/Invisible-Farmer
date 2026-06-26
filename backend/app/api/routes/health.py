from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["Health"])


@router.get("/", operation_id="root")
def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "version": settings.API_VERSION,
        "message": "Invisible Farmer Credit Review Agent backend is running."
    }


@router.get("/health", operation_id="health_check")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION
    }
