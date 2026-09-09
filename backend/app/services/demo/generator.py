"""Synthetic Demo Data Generator for Personal Mailtrack. (PRD Requirement 14)."""

from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.profiles import Profile
from app.models.tracked_emails import TrackedEmail, EmailRecipient, TrackedLink
from app.models.contacts import Contact
from app.models.campaigns import Campaign, CampaignRecipient
from app.models.documents import Document, DocumentShare, DocumentEvent
from app.models.events import OpenEvent, ClickEvent, ReplyEvent, ActivityEvent
from app.security.tracking_tokens import token_manager


async def seed_demo_data(session: AsyncSession, user_id: str) -> dict:
    """Generates rich, realistic synthetic activity for dashboard exploration."""
    now = datetime.now(timezone.utc)

    # 1. Seed Contacts
    demo_contacts = [
        {"name": "Sarah Connor", "email": "sarah.c@techventure.com", "company": "Tech Ventures", "score": 85, "status": "Hot"},
        {"name": "David Miller", "email": "d.miller@summitpartners.io", "company": "Summit Partners", "score": 42, "status": "Warm"},
        {"name": "Elena Rostova", "email": "elena@apexcloud.net", "company": "Apex Cloud", "score": 10, "status": "Cold"},
    ]
    created_contacts = []
    for c in demo_contacts:
        existing = (await session.execute(select(Contact).where(Contact.user_id == user_id, Contact.email == c["email"]))).scalars().first()
        if not existing:
            contact = Contact(
                user_id=user_id,
                email=c["email"],
                name=c["name"],
                company=c["company"],
                engagement_score=c["score"],
                status=c["status"],
                last_contacted_at=now - timedelta(days=2),
                last_opened_at=now - timedelta(hours=3),
            )
            session.add(contact)
            await session.flush()
            created_contacts.append(contact)
        else:
            created_contacts.append(existing)

    # 2. Seed Tracked Emails
    email_scenarios = [
        {
            "subject": "Series A Investment Terms & Timeline",
            "recipients": ["sarah.c@techventure.com"],
            "hours_ago": 4,
            "opens": 5,
            "clicks": 2,
            "replied": True,
            "is_hot": True,
        },
        {
            "subject": "Personal Mailtrack Implementation Review",
            "recipients": ["d.miller@summitpartners.io"],
            "hours_ago": 18,
            "opens": 2,
            "clicks": 1,
            "replied": False,
            "is_hot": False,
        },
        {
            "subject": "Partnership Introduction & Product Deck",
            "recipients": ["elena@apexcloud.net"],
            "hours_ago": 72,
            "opens": 0,
            "clicks": 0,
            "replied": False,
            "is_hot": False,
        },
    ]

    for sc in email_scenarios:
        sent_time = now - timedelta(hours=sc["hours_ago"])
        email = TrackedEmail(
            user_id=user_id,
            subject=sc["subject"],
            sent_at=sent_time,
        )
        session.add(email)
        await session.flush()

        # Recipient
        recip_email = sc["recipients"][0]
        recip = EmailRecipient(
            tracked_email_id=email.id,
            email=recip_email,
            raw_open_count=sc["opens"],
            human_open_count=sc["opens"],
            human_click_count=sc["clicks"],
            first_open_at=sent_time + timedelta(minutes=12) if sc["opens"] > 0 else None,
            last_open_at=sent_time + timedelta(minutes=45) if sc["opens"] > 0 else None,
            first_click_at=sent_time + timedelta(minutes=15) if sc["clicks"] > 0 else None,
            last_click_at=sent_time + timedelta(minutes=16) if sc["clicks"] > 0 else None,
            reply_received_at=sent_time + timedelta(hours=1) if sc["replied"] else None,
        )
        session.add(recip)
        await session.flush()

        # Activity events
        session.add(ActivityEvent(
            user_id=user_id,
            event_type="email.sent",
            entity_type="tracked_email",
            entity_id=email.id,
            source="compose_extension",
            metadata={"subject": sc["subject"], "recipient_email": recip_email},
            occurred_at=sent_time,
        ))

        if sc["opens"] > 0:
            session.add(ActivityEvent(
                user_id=user_id,
                event_type="email.opened",
                entity_type="email_recipient",
                entity_id=recip.id,
                source="tracking_pixel",
                metadata={"subject": sc["subject"], "recipient_email": recip_email, "classification": "human_likely"},
                occurred_at=sent_time + timedelta(minutes=12),
            ))

        if sc["clicks"] > 0:
            session.add(ActivityEvent(
                user_id=user_id,
                event_type="email.clicked",
                entity_type="email_recipient",
                entity_id=recip.id,
                source="tracking_redirect",
                metadata={"subject": sc["subject"], "destination_url": "https://example.com/proposal"},
                occurred_at=sent_time + timedelta(minutes=15),
            ))

        if sc["replied"]:
            session.add(ActivityEvent(
                user_id=user_id,
                event_type="email.replied",
                entity_type="email_recipient",
                entity_id=recip.id,
                source="gmail_sync",
                metadata={"subject": sc["subject"], "recipient_email": recip_email},
                occurred_at=sent_time + timedelta(hours=1),
            ))

    # 3. Seed Document
    doc = Document(
        user_id=user_id,
        title="Personal Mailtrack Architecture Spec.pdf",
        filename="architecture_spec.pdf",
        file_path="./storage/documents/demo.pdf",
        file_size_bytes=1024 * 340,
        total_pages=4,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    session.add(doc)
    await session.flush()

    share = DocumentShare(
        document_id=doc.id,
        recipient_email="sarah.c@techventure.com",
        watermark_text="CONFIDENTIAL - Tech Ventures",
    )
    session.add(share)
    await session.flush()

    # Seed page views
    for p, dur in [(1, 14.5), (2, 35.2), (3, 62.0), (4, 18.1)]:
        session.add(DocumentEvent(
            document_share_id=share.id,
            page_number=p,
            duration_seconds=dur,
            occurred_at=now - timedelta(hours=2),
        ))

    session.add(ActivityEvent(
        user_id=user_id,
        event_type="document.viewed",
        entity_type="document",
        entity_id=doc.id,
        source="pdf_viewer",
        metadata={"title": doc.title, "recipient_email": "sarah.c@techventure.com"},
        occurred_at=now - timedelta(hours=2),
    ))

    await session.commit()
    return {"status": "seeded", "contacts": len(demo_contacts), "emails": len(email_scenarios)}
