"""Notification rules and dispatched notification logs."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin, utc_now


class NotificationRule(Base, UUIDMixin, TimestampMixin):
    """Configurable notification trigger."""
    __tablename__ = "notification_rules"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    rule_type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # first_open, every_open, first_click, hot_conversation, revival, no_reply, doc_viewed
    channel: Mapped[str] = mapped_column(
        String(32), default="desktop", nullable=False
    )  # desktop, dashboard, webhook, email
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    conditions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class NotificationEvent(Base, UUIDMixin):
    """Log of dispatched user notifications."""
    __tablename__ = "notification_events"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    rule_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("notification_rules.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(32), default="desktop", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
