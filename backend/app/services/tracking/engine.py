"""Ultra-lightweight tracking engine for pixel opens and link redirects."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.events import ClickEvent, OpenEvent
from app.models.tracked_emails import EmailRecipient, TrackedEmail, TrackedLink
from app.security.tracking_tokens import token_manager
from app.security.url_safety import normalize_url, validate_destination_url
from app.services.events.bus import activity_bus
from app.services.tracking.classifier import EventClassifier

# 1x1 Transparent GIF binary payload
TRANSPARENT_GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
    b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)

PIXEL_HEADERS = {
    "Content-Type": "image/gif",
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "X-Content-Type-Options": "nosniff",
}


class TrackingEngine:
    """Core tracking service for opens and link clicks."""

    @staticmethod
    async def process_open(
        token: str,
        ip_address: str | None,
        user_agent: str | None,
        session: AsyncSession,
    ) -> bytes:
        """
        Processes open tracking pixel request.
        Always returns 1x1 transparent GIF. Fails silent on invalid token.
        """
        payload = token_manager.verify_open_token(token)
        if not payload:
            return TRANSPARENT_GIF_BYTES

        recipient_id = payload.get("rid")

        # Lookup recipient and parent email
        stmt = (
            select(EmailRecipient, TrackedEmail)
            .join(TrackedEmail, EmailRecipient.tracked_email_id == TrackedEmail.id)
            .where(EmailRecipient.id == recipient_id)
        )
        result = await session.execute(stmt)
        row = result.first()
        if not row:
            return TRANSPARENT_GIF_BYTES

        recipient, email = row
        occurred_at = datetime.now(UTC)

        # Classify open
        classification, confidence, reason = EventClassifier.classify_open(
            sent_at=email.sent_at,
            occurred_at=occurred_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        # Record raw open event
        open_event = OpenEvent(
            recipient_id=recipient.id,
            occurred_at=occurred_at,
            ip_address=ip_address,
            user_agent=user_agent,
            classification=classification,
            confidence=confidence,
            classification_reason=reason,
        )
        session.add(open_event)

        # Update recipient statistics
        if not recipient.first_open_at:
            recipient.first_open_at = occurred_at
        recipient.last_open_at = occurred_at
        recipient.raw_open_count += 1

        if classification == "human_likely":
            recipient.human_open_count += 1

        # Project to universal activity timeline
        await activity_bus.record_activity(
            session=session,
            user_id=email.user_id,
            event_type="email.opened",
            entity_type="email_recipient",
            entity_id=recipient.id,
            source="tracking_pixel",
            metadata={
                "subject": email.subject,
                "recipient_email": recipient.email,
                "classification": classification,
                "confidence": confidence,
                "reason": reason,
            },
            occurred_at=occurred_at,
        )

        await session.commit()
        return TRANSPARENT_GIF_BYTES

    @staticmethod
    async def process_click(
        token: str,
        destination_url: str,
        ip_address: str | None,
        user_agent: str | None,
        session: AsyncSession,
    ) -> str | None:
        """
        Validates token and destination URL, logs click event, and returns safe redirect destination.
        Returns None if token is invalid or URL is unsafe.
        """
        if not validate_destination_url(destination_url):
            return None

        clean_url = normalize_url(destination_url)
        recipient_id = token_manager.verify_click_token(token, clean_url)
        if not recipient_id:
            return None

        stmt = (
            select(EmailRecipient, TrackedEmail)
            .join(TrackedEmail, EmailRecipient.tracked_email_id == TrackedEmail.id)
            .where(EmailRecipient.id == recipient_id)
        )
        result = await session.execute(stmt)
        row = result.first()
        if not row:
            return None

        recipient, email = row
        occurred_at = datetime.now(UTC)

        # Check for matching tracked link
        link_stmt = select(TrackedLink).where(
            TrackedLink.tracked_email_id == email.id,
            TrackedLink.normalized_url == clean_url,
        )
        link_res = await session.execute(link_stmt)
        matched_link = link_res.scalars().first()

        # Record click event
        click_event = ClickEvent(
            recipient_id=recipient.id,
            tracked_link_id=matched_link.id if matched_link else None,
            destination_url=clean_url,
            occurred_at=occurred_at,
            ip_address=ip_address,
            user_agent=user_agent,
            classification="human_likely",
            confidence=1.0,
        )
        session.add(click_event)

        # Update recipient statistics
        if not recipient.first_click_at:
            recipient.first_click_at = occurred_at
        recipient.last_click_at = occurred_at
        recipient.human_click_count += 1

        # Project to universal activity timeline
        await activity_bus.record_activity(
            session=session,
            user_id=email.user_id,
            event_type="email.clicked",
            entity_type="email_recipient",
            entity_id=recipient.id,
            source="tracking_redirect",
            metadata={
                "subject": email.subject,
                "recipient_email": recipient.email,
                "destination_url": clean_url,
            },
            occurred_at=occurred_at,
        )

        await session.commit()
        return clean_url


tracking_engine = TrackingEngine()
