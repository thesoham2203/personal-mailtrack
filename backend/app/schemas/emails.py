"""Pydantic schemas for email tracking registration and queries."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RecipientInput(BaseModel):
    email: EmailStr
    name: str | None = None
    recipient_type: str = "to"  # to, cc, bcc


class EmailRegisterRequest(BaseModel):
    subject: str | None = None
    recipients: list[RecipientInput] = Field(min_length=1)
    links: list[str] = Field(default_factory=list)
    gmail_account_id: str | None = None
    gmail_message_id: str | None = None
    gmail_thread_id: str | None = None
    rfc_message_id: str | None = None


class TrackedLinkOutput(BaseModel):
    original_url: str
    tracked_url: str


class RecipientTrackingOutput(BaseModel):
    recipient_id: str
    email: str
    pixel_url: str


class EmailRegisterResponse(BaseModel):
    tracked_email_id: str
    public_id: str
    pixel_url: str  # Primary recipient pixel URL
    recipients: list[RecipientTrackingOutput]
    links: list[TrackedLinkOutput]


class RecipientDetail(BaseModel):
    id: str
    email: str
    name: str | None
    recipient_type: str
    first_open_at: datetime | None
    last_open_at: datetime | None
    first_click_at: datetime | None
    last_click_at: datetime | None
    raw_open_count: int
    human_open_count: int
    human_click_count: int
    reply_received_at: datetime | None
    bounced_at: datetime | None


class EmailDetailResponse(BaseModel):
    id: str
    public_id: str
    subject: str | None
    sent_at: datetime
    recipients: list[RecipientDetail]
    open_count: int  # Total opens
    human_open_count: int  # Verified human opens
    click_count: int
    has_replied: bool
    is_hot: bool
