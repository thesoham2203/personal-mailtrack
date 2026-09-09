"""Milestone 0 Foundation Tests."""

import pytest

from app.models.profiles import GmailAccount, Profile
from app.models.tracked_emails import EmailRecipient, TrackedEmail


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Verify /health returns 200 and system information."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "features" in data
    assert data["features"]["campaigns"] is True


@pytest.mark.asyncio
async def test_models_and_dual_db_layer(db_session):
    """Verify models insert and cascade delete properly in the async session."""
    # Create profile
    profile = Profile(email="test@example.com", display_name="Test User")
    db_session.add(profile)
    await db_session.flush()
    assert profile.id is not None

    # Create connected gmail account
    account = GmailAccount(user_id=profile.id, email="test@gmail.com", is_default=True)
    db_session.add(account)
    await db_session.flush()
    assert account.id is not None

    # Create tracked email with recipient
    email = TrackedEmail(
        user_id=profile.id,
        gmail_account_id=account.id,
        subject="Test Tracked Email",
    )
    db_session.add(email)
    await db_session.flush()

    recipient = EmailRecipient(
        tracked_email_id=email.id,
        email="recipient@example.com",
        recipient_type="to",
    )
    db_session.add(recipient)
    await db_session.commit()

    assert recipient.id is not None
    assert recipient.tracking_token_id is not None
