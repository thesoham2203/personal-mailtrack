"""Follow-up intelligence manager - purely DB-driven, no Gmail API required."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.events import OpenEvent
from app.models.tracked_emails import EmailRecipient, TrackedEmail


async def get_hot_conversations(
    db: AsyncSession,
    user_id: str,
    hours: float = 0.5,
    min_opens: int = 3,
) -> list[dict]:
    """
    Emails where human open_events count >= min_opens within last `hours` hours.
    Likely-human only (classification = 'human_likely').
    Join tracked_emails -> email_recipients -> open_events.
    Returns list with tracked_email_id, subject, recipient_email, open_count, last_open_at.
    """
    since = datetime.now(UTC) - timedelta(hours=hours)

    stmt = (
        select(
            TrackedEmail.id.label("tracked_email_id"),
            TrackedEmail.subject,
            EmailRecipient.email.label("recipient_email"),
            func.count(OpenEvent.id).label("open_count"),
            func.max(OpenEvent.occurred_at).label("last_open_at"),
        )
        .join(EmailRecipient, EmailRecipient.tracked_email_id == TrackedEmail.id)
        .join(OpenEvent, OpenEvent.recipient_id == EmailRecipient.id)
        .where(
            TrackedEmail.user_id == user_id,
            OpenEvent.occurred_at >= since,
            OpenEvent.classification == "human_likely",
        )
        .group_by(TrackedEmail.id, EmailRecipient.id)
        .having(func.count(OpenEvent.id) >= min_opens)
        .order_by(func.max(OpenEvent.occurred_at).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "tracked_email_id": row.tracked_email_id,
            "subject": row.subject,
            "recipient_email": row.recipient_email,
            "open_count": row.open_count,
            "last_open_at": row.last_open_at.isoformat() if row.last_open_at else None,
        }
        for row in rows
    ]


async def get_revival_alerts(
    db: AsyncSession,
    user_id: str,
    inactive_days: int = 7,
) -> list[dict]:
    """
    Emails where last open was more than inactive_days ago but there's a NEW
    open_event in the last 24 hours (recipient re-engaged after going cold).
    """
    cutoff = datetime.now(UTC) - timedelta(days=inactive_days)
    recent_window = datetime.now(UTC) - timedelta(hours=24)

    stmt = (
        select(
            TrackedEmail.id.label("tracked_email_id"),
            TrackedEmail.subject,
            EmailRecipient.email.label("recipient_email"),
            func.max(OpenEvent.occurred_at).label("last_open_at"),
        )
        .join(EmailRecipient, EmailRecipient.tracked_email_id == TrackedEmail.id)
        .join(OpenEvent, OpenEvent.recipient_id == EmailRecipient.id)
        .where(
            TrackedEmail.user_id == user_id,
        )
        .group_by(TrackedEmail.id, EmailRecipient.id)
        .having(
            func.max(OpenEvent.occurred_at) >= recent_window,
            func.min(OpenEvent.occurred_at) <= cutoff,
        )
        .order_by(func.max(OpenEvent.occurred_at).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "tracked_email_id": row.tracked_email_id,
            "subject": row.subject,
            "recipient_email": row.recipient_email,
            "last_open_at": row.last_open_at.isoformat() if row.last_open_at else None,
        }
        for row in rows
    ]


async def get_waiting_on_them(
    db: AsyncSession,
    user_id: str,
) -> list[dict]:
    """
    Tracked emails where reply_received_at IS NULL and sent_at < now()-48h.
    Join email_recipients for recipient info.
    """
    threshold = datetime.now(UTC) - timedelta(hours=48)

    stmt = (
        select(
            TrackedEmail.id.label("tracked_email_id"),
            TrackedEmail.subject,
            TrackedEmail.sent_at,
            EmailRecipient.email.label("recipient_email"),
            EmailRecipient.name.label("recipient_name"),
        )
        .join(EmailRecipient, EmailRecipient.tracked_email_id == TrackedEmail.id)
        .where(
            TrackedEmail.user_id == user_id,
            TrackedEmail.sent_at <= threshold,
            EmailRecipient.reply_received_at.is_(None),
        )
        .order_by(TrackedEmail.sent_at.asc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "tracked_email_id": row.tracked_email_id,
            "subject": row.subject,
            "sent_at": row.sent_at.isoformat() if row.sent_at else None,
            "recipient_email": row.recipient_email,
            "recipient_name": row.recipient_name,
        }
        for row in rows
    ]


async def get_no_reply_overdue(
    db: AsyncSession,
    user_id: str,
    threshold_hours: int = 48,
) -> list[dict]:
    """
    Same as get_waiting_on_them but sorted by age descending, threshold configurable.
    """
    threshold = datetime.now(UTC) - timedelta(hours=threshold_hours)

    stmt = (
        select(
            TrackedEmail.id.label("tracked_email_id"),
            TrackedEmail.subject,
            TrackedEmail.sent_at,
            EmailRecipient.email.label("recipient_email"),
            EmailRecipient.name.label("recipient_name"),
        )
        .join(EmailRecipient, EmailRecipient.tracked_email_id == TrackedEmail.id)
        .where(
            TrackedEmail.user_id == user_id,
            TrackedEmail.sent_at <= threshold,
            EmailRecipient.reply_received_at.is_(None),
        )
        .order_by(TrackedEmail.sent_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "tracked_email_id": row.tracked_email_id,
            "subject": row.subject,
            "sent_at": row.sent_at.isoformat() if row.sent_at else None,
            "recipient_email": row.recipient_email,
            "recipient_name": row.recipient_name,
        }
        for row in rows
    ]


async def get_waiting_on_me(
    db: AsyncSession,
    user_id: str,
) -> list[dict]:
    """
    Stub: returns empty list.
    Requires Gmail API reply sync to be configured.
    """
    # Requires Gmail API reply sync to be configured
    return []
