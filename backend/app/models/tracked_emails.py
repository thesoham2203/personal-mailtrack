"""Tracked emails, recipients, and tracked links models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.events import ClickEvent, OpenEvent


class TrackedEmail(Base, UUIDMixin, TimestampMixin):
    """Parent tracked email entity."""
    __tablename__ = "tracked_emails"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    gmail_account_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("gmail_accounts.id", ondelete="SET NULL"), index=True, nullable=True
    )
    public_id: Mapped[str] = mapped_column(
        String(36), default=generate_uuid, unique=True, index=True, nullable=False
    )
    gmail_message_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    gmail_thread_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    rfc_message_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )

    recipients: Mapped[list["EmailRecipient"]] = relationship(
        "EmailRecipient", back_populates="tracked_email", cascade="all, delete-orphan"
    )
    links: Mapped[list["TrackedLink"]] = relationship(
        "TrackedLink", back_populates="tracked_email", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_tracked_emails_user_sent", "user_id", "sent_at"),
    )


class EmailRecipient(Base, UUIDMixin):
    """Individual recipient of a tracked email."""
    __tablename__ = "email_recipients"

    tracked_email_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tracked_emails.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    contact_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recipient_type: Mapped[str] = mapped_column(String(16), default="to", nullable=False)  # to, cc, bcc
    tracking_token_id: Mapped[str] = mapped_column(
        String(36), default=generate_uuid, unique=True, index=True, nullable=False
    )
    first_open_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_open_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_click_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_click_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_open_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    human_open_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    human_click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reply_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    bounced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    tracked_email: Mapped["TrackedEmail"] = relationship("TrackedEmail", back_populates="recipients")
    open_events: Mapped[list["OpenEvent"]] = relationship(
        "OpenEvent", back_populates="recipient", cascade="all, delete-orphan"
    )
    click_events: Mapped[list["ClickEvent"]] = relationship(
        "ClickEvent", back_populates="recipient", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_recipients_email_created", "email", "created_at"),
    )


class TrackedLink(Base, UUIDMixin):
    """Link embedded in a tracked email."""
    __tablename__ = "tracked_links"

    tracked_email_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tracked_emails.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_url: Mapped[str] = mapped_column(Text, nullable=False)
    link_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    tracked_email: Mapped["TrackedEmail"] = relationship("TrackedEmail", back_populates="links")
