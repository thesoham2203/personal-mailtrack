"""API Router for registering and querying tracked emails."""

from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.contacts import Contact
from app.models.profiles import Profile
from app.models.tracked_emails import EmailRecipient, TrackedEmail, TrackedLink
from app.schemas.emails import (
    EmailDetailResponse,
    EmailRegisterRequest,
    EmailRegisterResponse,
    RecipientDetail,
    RecipientTrackingOutput,
    TrackedLinkOutput,
)
from app.security.tracking_tokens import token_manager
from app.security.url_safety import normalize_url, validate_destination_url
from app.services.events.bus import activity_bus

router = APIRouter(prefix="/api/v1/emails", tags=["Emails"])


async def get_current_user_id(db: AsyncSession = Depends(get_db)) -> str:
    """
    Returns default/current user_id.
    In standalone single-user personal mode, creates or retrieves the primary profile.
    In production with Supabase Auth, derives user_id from verified JWT.
    """
    stmt = select(Profile).limit(1)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        profile = Profile(email="owner@personal-mailtrack.local", display_name="Primary User")
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile.id


@router.post("", response_model=EmailRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_email(
    payload: EmailRegisterRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Registers a new outgoing email for tracking.
    Generates HMAC open tokens and signed click tokens.
    """
    tracked_email = TrackedEmail(
        user_id=user_id,
        gmail_account_id=payload.gmail_account_id,
        subject=payload.subject,
        gmail_message_id=payload.gmail_message_id,
        gmail_thread_id=payload.gmail_thread_id,
        rfc_message_id=payload.rfc_message_id,
    )
    db.add(tracked_email)
    await db.flush()

    recipient_outputs: list[RecipientTrackingOutput] = []
    primary_pixel_url = ""

    for idx, r in enumerate(payload.recipients):
        recipient = EmailRecipient(
            tracked_email_id=tracked_email.id,
            email=r.email.lower(),
            name=r.name,
            recipient_type=r.recipient_type,
        )
        db.add(recipient)
        await db.flush()

        # Update or create contact in CRM
        contact_stmt = select(Contact).where(Contact.user_id == user_id, Contact.email == recipient.email)
        c_res = await db.execute(contact_stmt)
        contact = c_res.scalars().first()
        if not contact:
            contact = Contact(
                user_id=user_id,
                email=recipient.email,
                name=recipient.name,
                status="Warm",
            )
            db.add(contact)
            await db.flush()

        # Generate signed open token
        open_token = token_manager.generate_open_token(
            recipient_id=recipient.id,
            tracked_email_id=tracked_email.id,
        )
        pixel_url = f"{settings.tracking_base_url}/t/o/{open_token}"
        if idx == 0:
            primary_pixel_url = pixel_url

        recipient_outputs.append(
            RecipientTrackingOutput(
                recipient_id=recipient.id,
                email=recipient.email,
                pixel_url=pixel_url,
            )
        )

    # Process and sign links (using primary recipient for standard send)
    primary_recipient_id = recipient_outputs[0].recipient_id if recipient_outputs else tracked_email.id
    link_outputs: list[TrackedLinkOutput] = []

    for pos, url in enumerate(payload.links):
        if not validate_destination_url(url):
            continue
        clean_url = normalize_url(url)
        tracked_link = TrackedLink(
            tracked_email_id=tracked_email.id,
            original_url=url,
            normalized_url=clean_url,
            position=pos,
        )
        db.add(tracked_link)

        # Generate HMAC signed click token
        click_token = token_manager.generate_click_token(
            recipient_id=primary_recipient_id,
            destination_url=clean_url,
        )
        encoded_dest = quote_plus(clean_url)
        tracked_url = f"{settings.tracking_base_url}/t/c/{click_token}?u={encoded_dest}"
        link_outputs.append(TrackedLinkOutput(original_url=url, tracked_url=tracked_url))

    # Project email.sent activity event
    await activity_bus.record_activity(
        session=db,
        user_id=user_id,
        event_type="email.sent",
        entity_type="tracked_email",
        entity_id=tracked_email.id,
        source="compose_extension",
        metadata={
            "subject": tracked_email.subject,
            "recipient_count": len(payload.recipients),
            "link_count": len(link_outputs),
        },
    )

    await db.commit()

    return EmailRegisterResponse(
        tracked_email_id=tracked_email.id,
        public_id=tracked_email.public_id,
        pixel_url=primary_pixel_url,
        recipients=recipient_outputs,
        links=link_outputs,
    )


@router.get("", response_model=list[EmailDetailResponse])
async def list_emails(
    filter_status: str | None = None,  # opened, unopened, clicked, replied, waiting_on_them
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists tracked emails with filters and engagement statistics."""
    stmt = (
        select(TrackedEmail)
        .where(TrackedEmail.user_id == user_id)
        .options(selectinload(TrackedEmail.recipients))
        .order_by(desc(TrackedEmail.sent_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    emails = result.scalars().all()

    response: list[EmailDetailResponse] = []
    for em in emails:
        recips = [
            RecipientDetail(
                id=r.id,
                email=r.email,
                name=r.name,
                recipient_type=r.recipient_type,
                first_open_at=r.first_open_at,
                last_open_at=r.last_open_at,
                first_click_at=r.first_click_at,
                last_click_at=r.last_click_at,
                raw_open_count=r.raw_open_count,
                human_open_count=r.human_open_count,
                human_click_count=r.human_click_count,
                reply_received_at=r.reply_received_at,
                bounced_at=r.bounced_at,
            )
            for r in em.recipients
        ]

        total_raw_opens = sum(r.raw_open_count for r in em.recipients)
        total_human_opens = sum(r.human_open_count for r in em.recipients)
        total_clicks = sum(r.human_click_count for r in em.recipients)
        has_replied = any(r.reply_received_at is not None for r in em.recipients)
        is_hot = total_human_opens >= 3

        # Apply in-memory filters if specified
        if filter_status == "opened" and total_raw_opens == 0:
            continue
        if filter_status == "unopened" and total_raw_opens > 0:
            continue
        if filter_status == "clicked" and total_clicks == 0:
            continue
        if filter_status == "replied" and not has_replied:
            continue
        if filter_status == "waiting_on_them" and has_replied:
            continue

        response.append(
            EmailDetailResponse(
                id=em.id,
                public_id=em.public_id,
                subject=em.subject,
                sent_at=em.sent_at,
                recipients=recips,
                open_count=total_raw_opens,
                human_open_count=total_human_opens,
                click_count=total_clicks,
                has_replied=has_replied,
                is_hot=is_hot,
            )
        )

    return response
