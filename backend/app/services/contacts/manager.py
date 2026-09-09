"""Contact engagement scoring and upsert service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contacts import Contact

SCORE_WEIGHTS: dict[str, int] = {
    "open": 1,
    "reopen": 2,
    "click": 5,
    "pdf_view": 5,
    "reply": 20,
    "bounce": -50,
    "unsubscribe": -100,
}


async def upsert_contact(
    db: AsyncSession,
    user_id: str,
    email: str,
    name: str | None = None,
) -> Contact:
    """Create or return existing contact."""
    result = await db.execute(
        select(Contact).where(Contact.user_id == user_id, Contact.email == email)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        contact = Contact(user_id=user_id, email=email, name=name or "")
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
    return contact


async def update_engagement_score(db: AsyncSession, contact_id: str, event_type: str) -> None:
    """Increment contact engagement score based on event type."""
    delta = SCORE_WEIGHTS.get(event_type, 0)
    if delta == 0:
        return
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if contact:
        contact.engagement_score = max(0, (contact.engagement_score or 0) + delta)
        # Classify status
        score = contact.engagement_score
        if score >= 30:
            contact.status = "hot"
        elif score >= 10:
            contact.status = "warm"
        else:
            contact.status = "cold"
        await db.commit()
