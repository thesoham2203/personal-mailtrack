"""Integration test for end-to-end email registration, pixel open, and link click."""

import pytest
from sqlalchemy import select

from app.models.events import ActivityEvent


@pytest.mark.asyncio
async def test_full_email_tracking_flow(client, db_session):
    # 1. Register an outgoing email with 2 recipients and 1 link
    reg_payload = {
        "subject": "Proposal for Q4 Strategy",
        "recipients": [
            {"email": "client@example.com", "name": "Client Name", "recipient_type": "to"},
            {"email": "partner@example.com", "name": "Partner", "recipient_type": "cc"},
        ],
        "links": ["https://example.com/proposal"],
    }
    res_reg = await client.post("/api/v1/emails", json=reg_payload)
    assert res_reg.status_code == 201
    data_reg = res_reg.json()

    tracked_email_id = data_reg["tracked_email_id"]
    pixel_url = data_reg["pixel_url"]
    tracked_links = data_reg["links"]

    assert len(data_reg["recipients"]) == 2
    assert len(tracked_links) == 1

    # Extract open token from pixel_url
    open_token = pixel_url.split("/t/o/")[-1]

    # 2. Simulate recipient opening email (loads 1x1 GIF)
    res_open = await client.get(
        f"/t/o/{open_token}",
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"},
    )
    assert res_open.status_code == 200
    assert res_open.headers["content-type"] == "image/gif"
    assert "no-store" in res_open.headers["cache-control"]
    assert res_open.content.startswith(b"GIF89a")

    # 3. Simulate clicking the tracked link
    tracked_link_url = tracked_links[0]["tracked_url"]
    # Path is /t/c/{token}?u=...
    link_path = tracked_link_url.replace("http://localhost:8000", "")

    res_click = await client.get(link_path, follow_redirects=False)
    assert res_click.status_code == 302
    assert res_click.headers["location"] == "https://example.com/proposal"

    # 4. Verify email query returns updated stats
    res_list = await client.get("/api/v1/emails")
    assert res_list.status_code == 200
    emails = res_list.json()
    assert len(emails) >= 1

    matching = next((e for e in emails if e["id"] == tracked_email_id), None)
    assert matching is not None
    assert matching["open_count"] == 1
    assert matching["click_count"] == 1

    # 5. Verify universal activity_events table has sent, opened, and clicked entries
    stmt = (
        select(ActivityEvent)
        .order_by(ActivityEvent.occurred_at.asc())
    )
    act_res = await db_session.execute(stmt)
    activities = act_res.scalars().all()
    event_types = [a.event_type for a in activities]

    assert "email.sent" in event_types
    assert "email.opened" in event_types
    assert "email.clicked" in event_types


@pytest.mark.asyncio
async def test_bot_scanner_open_distinction_and_activity_filtering(client, db_session):
    # 1. Register an email
    reg = await client.post(
        "/api/v1/emails",
        json={
            "subject": "Confidential Security Audit",
            "recipients": [{"email": "target@corp.com", "name": "Target", "recipient_type": "to"}],
        },
    )
    assert reg.status_code == 201
    reg_data = reg.json()
    email_id = reg_data["tracked_email_id"]
    open_token = reg_data["pixel_url"].split("/t/o/")[-1]

    # 2. Trigger an automated scanner open (Proofpoint)
    res_bot_1 = await client.get(
        f"/t/o/{open_token}",
        headers={"user-agent": "Proofpoint-AntiSpam/3.2"},
    )
    assert res_bot_1.status_code == 200

    # 3. Verify email listing: raw open is 1, but human open is 0
    res_list = await client.get("/api/v1/emails")
    emails = res_list.json()
    target = next(e for e in emails if e["id"] == email_id)
    assert target["open_count"] == 1
    assert target["human_open_count"] == 0

    # 4. Filter by opened: should NOT include target email because human opens == 0
    res_opened = await client.get("/api/v1/emails?filter_status=opened")
    assert not any(e["id"] == email_id for e in res_opened.json())

    # 5. Filter by unopened: SHOULD include target email
    res_unopened = await client.get("/api/v1/emails?filter_status=unopened")
    assert any(e["id"] == email_id for e in res_unopened.json())

    # 6. Test activity endpoint with filter_type=human vs all
    act_all = await client.get("/api/v1/analytics/activity")
    assert any(
        a["metadata"].get("recipient_email") == "target@corp.com"
        and a["metadata"].get("classification") == "security_scanner_likely"
        for a in act_all.json()
    )

    act_human = await client.get("/api/v1/analytics/activity?filter_type=human")
    assert not any(
        a["metadata"].get("recipient_email") == "target@corp.com"
        for a in act_human.json()
    )
