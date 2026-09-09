"""Simple automation rule evaluator skeleton."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automations import AutomationRule


async def evaluate_rules_for_event(
    db: AsyncSession,
    user_id: str,
    event_type: str,
    event_data: dict,
) -> list[str]:
    """
    Evaluate WHEN/IF/THEN rules for a given event.
    Returns list of triggered rule IDs.
    Stub: matches rules by event_trigger field.
    Future: evaluate rule.conditions_json against event_data.
    """
    result = await db.execute(
        select(AutomationRule).where(
            AutomationRule.user_id == user_id,
            AutomationRule.is_active.is_(True),
            AutomationRule.event_trigger == event_type,
        )
    )
    rules = result.scalars().all()
    triggered: list[str] = []
    for rule in rules:
        # Basic evaluation: if no conditions, trigger always
        # Future: evaluate rule.conditions_json against event_data
        triggered.append(str(rule.id))
    return triggered
