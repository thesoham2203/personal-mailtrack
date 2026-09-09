"""Auth router for personal single-user mode."""

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user_id
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user_id)):
    """Returns current user identity and feature status."""
    return {
        "user_id": user_id,
        "mode": "personal",
        "gmail_api_enabled": bool(settings.google_client_id),
    }
