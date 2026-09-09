"""API Router for Contact CRM management."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.contacts import Contact
from app.models.events import ActivityEvent
from app.routers.emails import get_current_user_id

router = APIRouter(prefix="/api/v1/contacts", tags=["Contacts CRM"])


class ContactCreateInput(BaseModel):
    email: EmailStr
    name: str | None = None
    company: str | None = None
    phone: str | None = None
    tags: str | None = None
    notes: str | None = None


class ContactUpdateInput(BaseModel):
    name: str | None = None
    company: str | None = None
    phone: str | None = None
    tags: str | None = None
    notes: str | None = None
    status: str | None = None


@router.get("")
async def list_contacts(
    search: str | None = None,
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists contacts sorted by engagement score."""
    stmt = (
        select(Contact)
        .where(Contact.user_id == user_id)
        .order_by(desc(Contact.engagement_score), desc(Contact.updated_at))
        .offset(offset)
        .limit(limit)
    )
    if search:
        search_pattern = f"%{search.lower()}%"
        stmt = stmt.where(Contact.email.ilike(search_pattern) | Contact.name.ilike(search_pattern))
    if status_filter:
        stmt = stmt.where(Contact.status == status_filter)

    result = await db.execute(stmt)
    contacts = result.scalars().all()

    return [
        {
            "id": c.id,
            "email": c.email,
            "name": c.name,
            "company": c.company,
            "phone": c.phone,
            "tags": c.tags.split(",") if c.tags else [],
            "engagement_score": c.engagement_score,
            "status": c.status,
            "last_contacted_at": c.last_contacted_at.isoformat() if c.last_contacted_at else None,
            "last_opened_at": c.last_opened_at.isoformat() if c.last_opened_at else None,
        }
        for c in contacts
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreateInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Creates a new contact."""
    existing = await db.execute(
        select(Contact).where(Contact.user_id == user_id, Contact.email == payload.email.lower())
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists.",
        )

    contact = Contact(
        user_id=user_id,
        email=payload.email.lower(),
        name=payload.name,
        company=payload.company,
        phone=payload.phone,
        tags=payload.tags,
        notes=payload.notes,
        status="Warm",
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.get("/{contact_id}")
async def get_contact_detail(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Retrieves contact profile and chronological interaction timeline."""
    contact = (
        await db.execute(select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id))
    ).scalars().first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    # Fetch activity timeline for this contact's email
    act_stmt = (
        select(ActivityEvent)
        .where(ActivityEvent.user_id == user_id)
        .order_by(desc(ActivityEvent.occurred_at))
        .limit(30)
    )
    all_acts = (await db.execute(act_stmt)).scalars().all()
    # Filter events where metadata recipient_email matches this contact
    timeline = [
        {
            "id": a.id,
            "event_type": a.event_type,
            "occurred_at": a.occurred_at.isoformat(),
            "source": a.source,
            "metadata": a.metadata_json or {},
        }
        for a in all_acts
        if (a.metadata_json or {}).get("recipient_email", "").lower() == contact.email.lower()
    ]

    return {
        "id": contact.id,
        "email": contact.email,
        "name": contact.name,
        "company": contact.company,
        "phone": contact.phone,
        "tags": contact.tags,
        "notes": contact.notes,
        "engagement_score": contact.engagement_score,
        "status": contact.status,
        "timeline": timeline,
    }


@router.patch("/{contact_id}")
async def update_contact(
    contact_id: str,
    payload: ContactUpdateInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Updates contact fields."""
    contact = (
        await db.execute(select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id))
    ).scalars().first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(contact, field, val)

    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Deletes a contact."""
    contact = (
        await db.execute(select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id))
    ).scalars().first()
    if contact:
        await db.delete(contact)
        await db.commit()
