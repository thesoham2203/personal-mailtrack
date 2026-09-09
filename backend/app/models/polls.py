"""Polls and tracked surveys models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin, utc_now


class Poll(Base, UUIDMixin, TimestampMixin):
    """Email embedded interactive poll."""
    __tablename__ = "polls"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question: Mapped[str] = mapped_column(String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    options: Mapped[list["PollOption"]] = relationship(
        "PollOption", back_populates="poll", cascade="all, delete-orphan"
    )
    responses: Mapped[list["PollResponse"]] = relationship(
        "PollResponse", back_populates="poll", cascade="all, delete-orphan"
    )


class PollOption(Base, UUIDMixin):
    """Option for a poll."""
    __tablename__ = "poll_options"

    poll_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("polls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    option_text: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(default=0, nullable=False)

    poll: Mapped["Poll"] = relationship("Poll", back_populates="options")


class PollResponse(Base, UUIDMixin):
    """Vote response recorded from tracked link."""
    __tablename__ = "poll_responses"

    poll_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("polls.id", ondelete="CASCADE"), index=True, nullable=False
    )
    option_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("poll_options.id", ondelete="CASCADE"), index=True, nullable=False
    )
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    responded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    poll: Mapped["Poll"] = relationship("Poll", back_populates="responses")
