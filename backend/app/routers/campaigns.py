"""API Router for Mail-Merge Campaigns and Safe Personalization."""

import re
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.campaigns import Campaign, CampaignRecipient
from app.models.tracked_emails import EmailRecipient, TrackedEmail
from app.routers.emails import get_current_user_id

router = APIRouter(prefix="/api/v1/campaigns", tags=["Campaigns"])


class CampaignRecipientInput(BaseModel):
    email: EmailStr
    data: dict[str, Any] = Field(default_factory=dict)


class CampaignCreateInput(BaseModel):
    name: str
    subject: str
    body_html: str
    batch_size: int = 10
    delay_seconds: int = 5
    recipients: list[CampaignRecipientInput] = Field(min_length=1)


def render_personalized_template(template: str, variables: dict[str, Any]) -> str:
    """
    Safely renders template variables with fallback support:
    e.g. {{first_name | fallback: "friend"}} or {{company}}
    (PRD Section 32)
    """
    def replace_var(match: re.Match) -> str:
        expression = match.group(1).strip()
        if "|" in expression:
            parts = expression.split("|", 1)
            var_name = parts[0].strip()
            fallback_part = parts[1].strip()
            fallback_match = re.search(r'fallback\s*:\s*["\'](.*?)["\']', fallback_part)
            fallback_val = fallback_match.group(1) if fallback_match else ""
            return str(variables.get(var_name) or fallback_val)
        return str(variables.get(expression, ""))

    return re.sub(r"\{\{(.*?)\}\}", replace_var, template)


@router.get("")
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists all mail-merge campaigns and statuses."""
    stmt = (
        select(Campaign)
        .where(Campaign.user_id == user_id)
        .options(selectinload(Campaign.recipients))
        .order_by(desc(Campaign.created_at))
    )
    result = await db.execute(stmt)
    campaigns = result.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "subject": c.subject,
            "status": c.status,
            "total_recipients": len(c.recipients),
            "sent_count": sum(1 for r in c.recipients if r.status == "sent"),
            "created_at": c.created_at.isoformat(),
        }
        for c in campaigns
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreateInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Creates a new mail merge campaign."""
    campaign = Campaign(
        user_id=user_id,
        name=payload.name,
        subject=payload.subject,
        body_html=payload.body_html,
        batch_size=payload.batch_size,
        delay_seconds=payload.delay_seconds,
        status="draft",
    )
    db.add(campaign)
    await db.flush()

    for r in payload.recipients:
        recip = CampaignRecipient(
            campaign_id=campaign.id,
            email=r.email.lower(),
            personalized_data=r.data,
            status="pending",
        )
        db.add(recip)

    await db.commit()
    await db.refresh(campaign)
    return {"id": campaign.id, "name": campaign.name, "status": campaign.status}


@router.get("/{campaign_id}/preview")
async def preview_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Previews personalized output for the first few recipients."""
    stmt = (
        select(Campaign)
        .where(Campaign.id == campaign_id, Campaign.user_id == user_id)
        .options(selectinload(Campaign.recipients))
    )
    res = await db.execute(stmt)
    campaign = res.scalars().first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")

    previews = []
    for r in campaign.recipients[:5]:
        var_data = r.personalized_data or {}
        var_data.setdefault("email", r.email)
        rendered_subject = render_personalized_template(campaign.subject, var_data)
        rendered_body = render_personalized_template(campaign.body_html, var_data)
        previews.append({
            "email": r.email,
            "subject": rendered_subject,
            "body_html": rendered_body,
        })

    return {"campaign_id": campaign.id, "previews": previews}


@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Executes campaign dispatch with individualized tracking identities per recipient.
    (PRD Section 10, 33)
    """
    stmt = (
        select(Campaign)
        .where(Campaign.id == campaign_id, Campaign.user_id == user_id)
        .options(selectinload(Campaign.recipients))
    )
    res = await db.execute(stmt)
    campaign = res.scalars().first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")

    campaign.status = "sending"
    campaign.started_at = datetime.now(UTC)
    await db.flush()

    # Generate individualized tracked email records for each pending recipient
    for r in campaign.recipients:
        if r.status != "pending":
            continue

        var_data = r.personalized_data or {}
        var_data.setdefault("email", r.email)
        rendered_subject = render_personalized_template(campaign.subject, var_data)

        # Create child tracked email
        tracked_email = TrackedEmail(
            user_id=user_id,
            subject=rendered_subject,
            campaign_id=campaign.id,
        )
        db.add(tracked_email)
        await db.flush()

        email_recip = EmailRecipient(
            tracked_email_id=tracked_email.id,
            email=r.email,
            recipient_type="to",
        )
        db.add(email_recip)
        await db.flush()

        r.tracked_email_id = tracked_email.id
        r.status = "sent"
        r.sent_at = datetime.now(UTC)

    campaign.status = "completed"
    campaign.completed_at = datetime.now(UTC)
    await db.commit()

    return {"status": "completed", "campaign_id": campaign.id}
