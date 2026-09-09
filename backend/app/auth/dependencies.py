"""Auth dependencies for personal single-user mode."""

from fastapi import Header, HTTPException

from app.config import settings


async def get_current_user_id(x_api_key: str = Header(default="")) -> str:
    """
    For personal local use: if EXTENSION_API_KEY is set in settings, validate it.
    If not set, allow all requests (development mode).
    Returns a fixed user_id string (personal single-user).
    """
    if settings.extension_api_key and x_api_key != settings.extension_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return settings.personal_user_id
