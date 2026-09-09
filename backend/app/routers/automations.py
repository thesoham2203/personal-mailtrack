"""Automation rules management endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.database import get_db
from app.models.automations import AutomationRule

router = APIRouter(prefix="/api/v1/automations", tags=["automations"])


@router.get("/")
async def list_automations(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists automation rules for the current user."""
    result = await db.execute(
        select(AutomationRule).where(AutomationRule.user_id == user_id)
    )
    rules = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "trigger_event": r.event_trigger,
            "is_active": r.is_active,
        }
        for r in rules
    ]


class AutomationCreate(BaseModel):
    name: str
    trigger_event: str
    conditions: dict = {}
    actions: list = []


@router.post("/")
async def create_automation(
    body: AutomationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Creates a new automation rule."""
    rule = AutomationRule(
        user_id=user_id,
        name=body.name,
        event_trigger=body.trigger_event,
        conditions_json=body.conditions,
        actions_json={"actions": body.actions},
        is_active=True,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return {"id": str(rule.id), "name": rule.name}
