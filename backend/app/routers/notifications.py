"""Notification rules management endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.database import get_db
from app.models.notifications import NotificationRule

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/rules")
async def list_rules(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists notification rules for the current user."""
    result = await db.execute(
        select(NotificationRule).where(NotificationRule.user_id == user_id)
    )
    rules = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "rule_type": r.rule_type,
            "channel": r.channel,
            "enabled": r.is_enabled,
        }
        for r in rules
    ]
