"""Follow-up intelligence endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.database import get_db
from app.services.followup.manager import (
    get_hot_conversations,
    get_no_reply_overdue,
    get_revival_alerts,
    get_waiting_on_me,
    get_waiting_on_them,
)

router = APIRouter(prefix="/api/v1/followup", tags=["followup"])


@router.get("/hot")
async def hot_conversations(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Returns emails with multiple opens in the last 30 minutes (hot conversations)."""
    return await get_hot_conversations(db, user_id)


@router.get("/revival")
async def revival_alerts(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Returns emails where a recipient re-engaged after 7+ days of inactivity."""
    return await get_revival_alerts(db, user_id)


@router.get("/waiting-on-them")
async def waiting_on_them(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Returns emails sent 48h+ ago with no reply received."""
    return await get_waiting_on_them(db, user_id)


@router.get("/no-reply")
async def no_reply_overdue(
    hours: int = 48,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Returns emails with no reply, sorted by age (oldest first). Threshold configurable."""
    return await get_no_reply_overdue(db, user_id, threshold_hours=hours)


@router.get("/waiting-on-me")
async def waiting_on_me(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Returns emails where user has not replied (requires Gmail API sync)."""
    return await get_waiting_on_me(db, user_id)
