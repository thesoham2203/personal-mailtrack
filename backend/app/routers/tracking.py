"""Public tracking endpoints for email opens and link redirects."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.security.tracking_tokens import token_manager
from app.services.tracking.engine import PIXEL_HEADERS, tracking_engine

router = APIRouter(tags=["Tracking"])


@router.get("/t/o/{token}", summary="Tracking Pixel Open Endpoint")
async def track_open(token: str, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Returns 1x1 transparent GIF and records open event.
    Ultra-lightweight, non-blocking, fail-silent.
    """
    ip_address = request.headers.get("x-forwarded-for", request.client.host if request.client else None)
    if ip_address and "," in ip_address:
        ip_address = ip_address.split(",")[0].strip()

    user_agent = request.headers.get("user-agent")

    gif_bytes = await tracking_engine.process_open(
        token=token,
        ip_address=ip_address,
        user_agent=user_agent,
        session=db,
    )
    return Response(content=gif_bytes, media_type="image/gif", headers=PIXEL_HEADERS)


@router.get("/t/c/{token}", summary="Tracked Link Click Redirect Endpoint")
async def track_click(
    token: str,
    u: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Validates capability token and destination URL, records click event,
    and returns HTTP 302 redirect. Rejects SSRF and malformed URLs.
    """
    ip_address = request.headers.get("x-forwarded-for", request.client.host if request.client else None)
    if ip_address and "," in ip_address:
        ip_address = ip_address.split(",")[0].strip()

    user_agent = request.headers.get("user-agent")

    destination_url = await tracking_engine.process_click(
        token=token,
        destination_url=u,
        ip_address=ip_address,
        user_agent=user_agent,
        session=db,
    )

    if not destination_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_OR_UNSAFE_REDIRECT", "message": "Invalid tracking link or destination."}},
        )

    return RedirectResponse(url=destination_url, status_code=status.HTTP_302_FOUND)


@router.get("/u/{token}", summary="Unsubscribe Endpoint")
async def unsubscribe(token: str, db: AsyncSession = Depends(get_db)):
    """Handles 1-click campaign unsubscription."""
    payload = token_manager.verify_unsubscribe_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_UNSUBSCRIBE_TOKEN", "message": "Invalid or expired link."}},
        )

    email = payload.get("em")
    return {
        "status": "unsubscribed",
        "email": email,
        "message": f"{email} has been successfully unsubscribed from future campaigns.",
    }
