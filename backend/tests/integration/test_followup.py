"""Integration tests for the follow-up manager."""

import pytest

from app.services.followup.manager import get_no_reply_overdue, get_waiting_on_them


@pytest.mark.asyncio
async def test_waiting_on_them_returns_list(db_session):
    """Should return a list (may be empty in test environment)."""
    result = await get_waiting_on_them(db_session, "00000000-0000-0000-0000-000000000001")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_no_reply_overdue_returns_list(db_session):
    """Should return a list (may be empty in test environment)."""
    result = await get_no_reply_overdue(db_session, "00000000-0000-0000-0000-000000000001")
    assert isinstance(result, list)
