"""API Router for productivity analytics, universal activity stream, and delivery certificates."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.events import ActivityEvent
from app.models.tracked_emails import EmailRecipient, TrackedEmail
from app.routers.emails import get_current_user_id

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_summary_metrics(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Computes high-level productivity metrics."""
    cutoff = datetime.now(UTC) - timedelta(days=days)

    # Total emails sent
    stmt_emails = select(func.count(TrackedEmail.id)).where(
        TrackedEmail.user_id == user_id,
        TrackedEmail.sent_at >= cutoff,
    )
    total_sent = (await db.execute(stmt_emails)).scalar() or 0

    # Total recipients
    stmt_recips = (
        select(EmailRecipient)
        .join(TrackedEmail, EmailRecipient.tracked_email_id == TrackedEmail.id)
        .where(TrackedEmail.user_id == user_id, TrackedEmail.sent_at >= cutoff)
    )
    recipients = (await db.execute(stmt_recips)).scalars().all()

    total_recipients = len(recipients)
    total_raw_opens = sum(r.raw_open_count for r in recipients)
    total_human_opens = sum(r.human_open_count for r in recipients)
    total_clicks = sum(r.human_click_count for r in recipients)
    total_replies = sum(1 for r in recipients if r.reply_received_at is not None)

    open_rate = (total_human_opens / total_recipients * 100) if total_recipients > 0 else 0.0
    click_rate = (total_clicks / total_recipients * 100) if total_recipients > 0 else 0.0
    reply_rate = (total_replies / total_recipients * 100) if total_recipients > 0 else 0.0

    return {
        "period_days": days,
        "total_sent": total_sent,
        "total_recipients": total_recipients,
        "total_raw_opens": total_raw_opens,
        "total_human_opens": total_human_opens,
        "total_clicks": total_clicks,
        "total_replies": total_replies,
        "open_rate_percent": round(open_rate, 1),
        "click_rate_percent": round(click_rate, 1),
        "reply_rate_percent": round(reply_rate, 1),
    }


@router.get("/activity")
async def get_activity_stream(
    limit: int = 50,
    offset: int = 0,
    event_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Reconciliation & live feed endpoint returning universal chronological activity events."""
    stmt = (
        select(ActivityEvent)
        .where(ActivityEvent.user_id == user_id)
        .order_by(desc(ActivityEvent.occurred_at))
        .offset(offset)
        .limit(limit)
    )
    if event_type:
        stmt = stmt.where(ActivityEvent.event_type == event_type)

    result = await db.execute(stmt)
    activities = result.scalars().all()

    return [
        {
            "id": a.id,
            "event_type": a.event_type,
            "source": a.source,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "occurred_at": a.occurred_at.isoformat(),
            "metadata": a.metadata_json or {},
        }
        for a in activities
    ]


@router.get("/certificate/{tracked_email_id}")
async def get_certified_evidence_report(
    tracked_email_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Generates a certified delivery evidence report (PRD Section 48) containing
    message identifiers, sent timestamps, recipient events, and hash evidence.
    """
    stmt = select(TrackedEmail).where(
        TrackedEmail.id == tracked_email_id,
        TrackedEmail.user_id == user_id,
    )
    res = await db.execute(stmt)
    email = res.scalars().first()
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found.")

    # Fetch recipients
    r_stmt = select(EmailRecipient).where(EmailRecipient.tracked_email_id == email.id)
    recipients = (await db.execute(r_stmt)).scalars().all()

    return {
        "certificate_id": email.public_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "disclaimer": "Tracking evidence confirms resource retrieval by client software; it does not constitute legal proof of comprehension.",
        "email": {
            "id": email.id,
            "subject": email.subject,
            "sent_at": email.sent_at.isoformat(),
            "gmail_message_id": email.gmail_message_id,
            "gmail_thread_id": email.gmail_thread_id,
            "rfc_message_id": email.rfc_message_id,
        },
        "recipients": [
            {
                "email": r.email,
                "name": r.name,
                "first_open_at": r.first_open_at.isoformat() if r.first_open_at else None,
                "last_open_at": r.last_open_at.isoformat() if r.last_open_at else None,
                "human_open_count": r.human_open_count,
                "click_count": r.human_click_count,
                "reply_received_at": r.reply_received_at.isoformat() if r.reply_received_at else None,
            }
            for r in recipients
        ],
    }
