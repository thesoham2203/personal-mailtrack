"""User preferences and system settings model."""

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class UserSettings(Base, UUIDMixin, TimestampMixin):
    """Personal user tracking and privacy preferences."""
    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    privacy_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    store_ip_address: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    store_user_agent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    desktop_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sound_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    no_reply_threshold_hours: Mapped[int] = mapped_column(Integer, default=48, nullable=False)
    hot_conversation_opens: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    hot_conversation_window_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    revival_threshold_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    custom_settings_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
