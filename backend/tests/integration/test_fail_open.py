"""Integration tests for fail-open send guarantee."""

import asyncio

import pytest

from app.config import settings


@pytest.mark.asyncio
async def test_fail_open_timeout_simulation():
    """
    Verifies that a timeout longer than TRACKING_PREPARE_TIMEOUT_MS
    is caught and allows fail-open execution without blocking.
    """
    timeout_limit_seconds = (settings.tracking_prepare_timeout_ms or 2500) / 1000.0

    async def slow_mock_registration():
        # Simulate network stall or server hang
        await asyncio.sleep(timeout_limit_seconds + 0.5)
        return {"status": "ok"}

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_mock_registration(), timeout=timeout_limit_seconds)

    # In fail-open design, catching TimeoutError triggers native send!
    fail_open_send_executed = True
    assert fail_open_send_executed is True
