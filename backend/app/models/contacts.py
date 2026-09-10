"""Lightweight Contact CRM models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import GUID, TimestampMixin, UUIDMixin


class Contact(Base, UUIDMixin, TimestampMixin):
    """Personal contact record."""
    __tablename__ = "contacts"

    user_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated or JSON string
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    engagement_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="Warm", nullable=False)  # Hot, Warm, Cold
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_clicked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    list_memberships: Mapped[list["ContactListMember"]] = relationship(
        "ContactListMember", back_populates="contact", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_contacts_user_email", "user_id", "email", unique=True),
    )


class ContactList(Base, UUIDMixin, TimestampMixin):
    """Segmented contact list for campaigns."""
    __tablename__ = "contact_lists"

    user_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    members: Mapped[list["ContactListMember"]] = relationship(
        "ContactListMember", back_populates="contact_list", cascade="all, delete-orphan"
    )


class ContactListMember(Base, UUIDMixin, TimestampMixin):
    """Membership join table."""
    __tablename__ = "contact_list_members"

    contact_list_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("contact_lists.id", ondelete="CASCADE"), index=True, nullable=False
    )
    contact_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("contacts.id", ondelete="CASCADE"), index=True, nullable=False
    )

    contact_list: Mapped["ContactList"] = relationship("ContactList", back_populates="members")
    contact: Mapped["Contact"] = relationship("Contact", back_populates="list_memberships")


class ContactNote(Base, UUIDMixin, TimestampMixin):
    """Chronological notes on a contact."""
    __tablename__ = "contact_notes"

    contact_id: Mapped[str] = mapped_column(
        GUID, ForeignKey("contacts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

