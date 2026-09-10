"""Model base mixins and common utilities."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column

GUID = Uuid(as_uuid=False)


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    """Provides created_at and updated_at timestamps in UTC."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class UUIDMixin:
    """Primary key UUID mixin compatible with SQLite and Postgres."""
    id: Mapped[str] = mapped_column(
        GUID,
        primary_key=True,
        default=generate_uuid,
        nullable=False,
    )

