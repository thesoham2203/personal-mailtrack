"""Gmail API management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.database import get_db
from app.models.profiles import GmailAccount
from app.services.gmail.auth import (
    exchange_code_for_tokens,
    get_oauth_authorization_url,
    is_gmail_api_enabled,
)
from app.services.gmail.sync import sync_replies_for_account

router = APIRouter(prefix="/api/v1/gmail", tags=["gmail"])


@router.get("/status")
async def gmail_status(user_id: str = Depends(get_current_user_id)):
    """Returns Gmail API configuration status."""
    return {
        "gmail_api_enabled": is_gmail_api_enabled(),
        "message": (
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env to enable Gmail API."
            if not is_gmail_api_enabled()
            else "Gmail API configured."
        ),
    }


@router.get("/auth-url")
async def get_auth_url(user_id: str = Depends(get_current_user_id)):
    """Returns the Google OAuth2 authorization URL."""
    url = get_oauth_authorization_url(user_id)
    if not url:
        raise HTTPException(status_code=501, detail="Gmail API credentials not configured.")
    return {"url": url}


@router.get("/callback")
async def oauth_callback(code: str, state: str, db: AsyncSession = Depends(get_db)):
    """Handles Google OAuth2 callback and token exchange."""
    tokens = await exchange_code_for_tokens(code)
    if not tokens:
        raise HTTPException(status_code=501, detail="Gmail API not configured.")
    return {"status": "ok", "note": "Token exchange succeeded. Store and link to gmail account."}


@router.get("/accounts")
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists connected Gmail accounts for the current user."""
    result = await db.execute(
        select(GmailAccount).where(GmailAccount.user_id == user_id)
    )
    accounts = result.scalars().all()
    return [
        {"id": str(a.id), "email": a.email, "is_default": a.is_default}
        for a in accounts
    ]


@router.post("/sync")
async def trigger_sync(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Triggers incremental Gmail reply sync."""
    result = await sync_replies_for_account(db, user_id)
    return result
