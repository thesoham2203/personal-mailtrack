"""Document and PDF tracking models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin, generate_uuid, utc_now


class Document(Base, UUIDMixin, TimestampMixin):
    """Uploaded PDF or document."""
    __tablename__ = "documents"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)  # Local path or Supabase Storage key
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(64), default="application/pdf", nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    total_pages: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    shares: Mapped[list["DocumentShare"]] = relationship(
        "DocumentShare", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentShare(Base, UUIDMixin, TimestampMixin):
    """Secure tracked share link for a document."""
    __tablename__ = "document_shares"

    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    share_token: Mapped[str] = mapped_column(
        String(64), default=generate_uuid, unique=True, index=True, nullable=False
    )
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recipient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    download_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    watermark_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="shares")
    events: Mapped[list["DocumentEvent"]] = relationship(
        "DocumentEvent", back_populates="share", cascade="all, delete-orphan"
    )


class DocumentEvent(Base, UUIDMixin):
    """Buffered page duration and document view logs."""
    __tablename__ = "document_events"

    document_share_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("document_shares.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(32), default="page_view", nullable=False
    )  # opened, page_view, downloaded, completed
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True, nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    share: Mapped["DocumentShare"] = relationship("DocumentShare", back_populates="events")

    __table_args__ = (
        Index("ix_doc_events_share_occurred", "document_share_id", "occurred_at"),
    )
