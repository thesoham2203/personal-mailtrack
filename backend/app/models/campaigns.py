"""Email campaigns and mail-merge models."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Campaign(Base, UUIDMixin, TimestampMixin):
    """Mail-merge email campaign."""
    __tablename__ = "campaigns"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    gmail_account_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("gmail_accounts.id", ondelete="SET NULL"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(512), nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="draft", index=True, nullable=False
    )  # draft, scheduled, sending, paused, completed, cancelled
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    batch_size: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    delay_seconds: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    recipients: Mapped[list["CampaignRecipient"]] = relationship(
        "CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan"
    )


class CampaignRecipient(Base, UUIDMixin, TimestampMixin):
    """Individual recipient in a campaign."""
    __tablename__ = "campaign_recipients"

    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True, nullable=False
    )
    contact_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("contacts.id", ondelete="SET NULL"), index=True, nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    personalized_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default="pending", index=True, nullable=False
    )  # pending, sent, failed, bounced, unsubscribed
    tracked_email_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("tracked_emails.id", ondelete="SET NULL"), index=True, nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="recipients")

    __table_args__ = (
        Index("ix_campaign_recip_status", "campaign_id", "status"),
    )


class EmailTemplate(Base, UUIDMixin, TimestampMixin):
    """Reusable email template with variables."""
    __tablename__ = "email_templates"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(512), nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_favorite: Mapped[bool] = mapped_column(default=False, nullable=False)
