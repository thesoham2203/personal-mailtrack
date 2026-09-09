"""User profile and account models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Profile(Base, UUIDMixin, TimestampMixin):
    """User profile aligned with Supabase Auth UID."""
    __tablename__ = "profiles"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)

    gmail_accounts: Mapped[list["GmailAccount"]] = relationship(
        "GmailAccount", back_populates="user", cascade="all, delete-orphan"
    )


class GmailAccount(Base, UUIDMixin, TimestampMixin):
    """Connected personal Gmail account."""
    __tablename__ = "gmail_accounts"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    google_account_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    picture_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["Profile"] = relationship("Profile", back_populates="gmail_accounts")
    oauth_credential: Mapped[Optional["OAuthCredential"]] = relationship(
        "OAuthCredential", back_populates="gmail_account", uselist=False, cascade="all, delete-orphan"
    )


class OAuthCredential(Base, UUIDMixin, TimestampMixin):
    """Encrypted OAuth refresh and access tokens."""
    __tablename__ = "oauth_credentials"

    gmail_account_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("gmail_accounts.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)

    gmail_account: Mapped["GmailAccount"] = relationship(
        "GmailAccount", back_populates="oauth_credential"
    )
