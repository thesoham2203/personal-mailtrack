"""Automation rules and Webhook delivery models."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import GUID, TimestampMixin, UUIDMixin, utc_now


class AutomationRule(Base, UUIDMixin, TimestampMixin):
    """Configurable WHEN/IF/THEN automation rule."""
    __tablename__ = "automation_rules"

    user_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    event_trigger: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # e.g. email.opened
    conditions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # IF conditions
    actions_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # THEN actions


class AutomationRun(Base, UUIDMixin):
    """Log of executed automation rules."""
    __tablename__ = "automation_runs"

    rule_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("automation_rules.id", ondelete="CASCADE"), index=True, nullable=False
    )
    activity_event_id: Mapped[str] = mapped_column(GUID, index=True, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="success", nullable=False)
    output_details: Mapped[str | None] = mapped_column(Text, nullable=True)


class WebhookEndpoint(Base, UUIDMixin, TimestampMixin):
    """Registered webhook destination."""
    __tablename__ = "webhook_endpoints"

    user_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    subscribed_events: Mapped[str] = mapped_column(
        Text, default="email.opened,email.clicked,email.replied", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WebhookDelivery(Base, UUIDMixin):
    """Delivery attempt log for webhooks."""
    __tablename__ = "webhook_deliveries"

    webhook_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_id: Mapped[str] = mapped_column(GUID, index=True, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
