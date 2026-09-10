"""Event models including universal ActivityEvent and domain-specific tracking events."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import GUID, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.tracked_emails import EmailRecipient


class OpenEvent(Base, UUIDMixin):
    """Raw open/pixel load event."""
    __tablename__ = "open_events"

    recipient_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("email_recipients.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    os_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Classification Layer
    classification: Mapped[str] = mapped_column(
        String(32), default="unknown", index=True, nullable=False
    )  # human_likely, proxy_likely, security_scanner_likely, automation_likely, unknown
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    classification_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    recipient: Mapped["EmailRecipient"] = relationship("EmailRecipient", back_populates="open_events")

    __table_args__ = (
        Index("ix_open_events_recip_occurred", "recipient_id", "occurred_at"),
    )


class ClickEvent(Base, UUIDMixin):
    """Raw link click event."""
    __tablename__ = "click_events"

    recipient_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("email_recipients.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tracked_link_id: Mapped[str | None] = mapped_column(
        GUID,
        ForeignKey("tracked_links.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    destination_url: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[str] = mapped_column(String(32), default="human_likely", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    recipient: Mapped["EmailRecipient"] = relationship("EmailRecipient", back_populates="click_events")

    __table_args__ = (
        Index("ix_click_events_recip_occurred", "recipient_id", "occurred_at"),
    )


class ReplyEvent(Base, UUIDMixin):
    """Correlated email reply event."""
    __tablename__ = "reply_events"

    recipient_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("email_recipients.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    gmail_message_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    rfc_message_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    in_reply_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )


class BounceEvent(Base, UUIDMixin):
    """Email delivery failure / bounce event."""
    __tablename__ = "bounce_events"

    recipient_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("email_recipients.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    bounce_type: Mapped[str] = mapped_column(String(32), default="hard", nullable=False)  # hard, soft
    smtp_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    diagnostic_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )


class ActivityEvent(Base, UUIDMixin):
    """Universal chronological activity event stream."""
    __tablename__ = "activity_events"

    user_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    # email.sent, email.opened, email.clicked, email.replied, email.bounced, document.viewed, campaign.completed
    source: Mapped[str] = mapped_column(String(64), default="tracking_engine", nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # email_recipient, document, campaign
    entity_id: Mapped[str] = mapped_column(GUID, index=True, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_activity_events_user_occurred", "user_id", "occurred_at"),
    )

