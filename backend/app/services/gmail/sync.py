"""Gmail incremental reply sync stub."""

from sqlalchemy.ext.asyncio import AsyncSession

from .auth import is_gmail_api_enabled


async def sync_replies_for_account(db: AsyncSession, gmail_account_id: str) -> dict:
    """
    Lightweight incremental reply sync.
    Returns {"status": "skipped", "reason": "..."} if Gmail API not configured.
    Future: use Gmail API history.list for incremental sync.
    """
    if not is_gmail_api_enabled():
        return {"status": "skipped", "reason": "Gmail API credentials not configured"}
    return {"status": "ok", "synced": 0, "note": "Gmail API sync stub - not yet implemented"}
