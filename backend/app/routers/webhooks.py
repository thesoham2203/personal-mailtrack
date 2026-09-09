"""Webhook endpoints management."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.database import get_db
from app.models.automations import WebhookEndpoint
from app.security.url_safety import validate_destination_url

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


class WebhookCreate(BaseModel):
    url: str
    events: list[str]
    secret: str = ""
    enabled: bool = True


@router.get("/")
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists registered webhook endpoints for the current user."""
    result = await db.execute(
        select(WebhookEndpoint).where(WebhookEndpoint.user_id == user_id)
    )
    webhooks = result.scalars().all()
    return [
        {
            "id": str(w.id),
            "url": w.url,
            "events": w.subscribed_events,
            "enabled": w.is_active,
        }
        for w in webhooks
    ]


@router.post("/")
async def create_webhook(
    body: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Registers a new webhook endpoint."""
    if not validate_destination_url(body.url):
        raise HTTPException(status_code=400, detail="Unsafe webhook URL rejected.")
    wh = WebhookEndpoint(
        user_id=user_id,
        url=body.url,
        subscribed_events=",".join(body.events),
        secret=body.secret,
        is_active=body.enabled,
    )
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return {"id": str(wh.id), "url": wh.url}


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Deletes a webhook endpoint."""
    result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.id == webhook_id,
            WebhookEndpoint.user_id == user_id,
        )
    )
    wh = result.scalar_one_or_none()
    if not wh:
        raise HTTPException(status_code=404, detail="Webhook not found.")
    await db.delete(wh)
    await db.commit()
    return {"status": "deleted"}
