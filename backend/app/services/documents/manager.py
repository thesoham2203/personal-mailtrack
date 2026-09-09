"""Document share access helpers."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import DocumentShare


async def get_share_by_token(db: AsyncSession, share_token: str) -> DocumentShare | None:
    """Look up a DocumentShare by its share token."""
    result = await db.execute(
        select(DocumentShare).where(DocumentShare.share_token == share_token)
    )
    return result.scalar_one_or_none()


async def is_share_accessible(share: DocumentShare) -> tuple[bool, str]:
    """Returns (accessible, reason)."""
    if share.expires_at and share.expires_at < datetime.now(UTC):
        return False, "expired"
    if not share.is_active:
        return False, "inactive"
    return True, "ok"
