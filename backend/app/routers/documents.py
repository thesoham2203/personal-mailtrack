"""API Router for Document & PDF Tracking, Secure Shares, and Hosted Viewer."""

import hashlib
import os
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.documents import Document, DocumentEvent, DocumentShare
from app.routers.emails import get_current_user_id
from app.services.events.bus import activity_bus

router = APIRouter(tags=["Documents & PDF Tracking"])

DOCS_STORAGE_DIR = "./storage/documents"
os.makedirs(DOCS_STORAGE_DIR, exist_ok=True)


class ShareCreateInput(BaseModel):
    recipient_email: str | None = None
    recipient_name: str | None = None
    expires_in_days: int | None = 30
    download_allowed: bool = True
    watermark_text: str | None = None


class BufferedDocEvent(BaseModel):
    event_type: str = "page_view"  # opened, page_view, downloaded, completed
    page_number: int | None = None
    duration_seconds: float = 0.0


class BufferedEventPayload(BaseModel):
    events: list[BufferedDocEvent]


# Authenticated API endpoints
@router.get("/api/v1/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lists tracked documents."""
    stmt = (
        select(Document)
        .where(Document.user_id == user_id)
        .options(selectinload(Document.shares))
        .order_by(desc(Document.created_at))
    )
    res = await db.execute(stmt)
    docs = res.scalars().all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "filename": d.filename,
            "file_size_bytes": d.file_size_bytes,
            "total_pages": d.total_pages,
            "shares_count": len(d.shares),
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.post("/api/v1/documents", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Uploads and registers a PDF document for tracking."""
    content = await file.read()
    if len(content) > (settings.max_upload_mb * 1024 * 1024):
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large.")

    sha256 = hashlib.sha256(content).hexdigest()
    storage_filename = f"{sha256}.pdf"
    storage_path = os.path.join(DOCS_STORAGE_DIR, storage_filename)

    with open(storage_path, "wb") as f:
        f.write(content)

    doc = Document(
        user_id=user_id,
        title=title or file.filename or "Untitled PDF",
        filename=file.filename or "document.pdf",
        file_path=storage_path,
        file_size_bytes=len(content),
        mime_type="application/pdf",
        sha256_hash=sha256,
        total_pages=5,  # Default pages estimate
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.post("/api/v1/documents/{document_id}/shares")
async def create_document_share(
    document_id: str,
    payload: ShareCreateInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Creates a secure tracked share link for a document."""
    stmt = select(Document).where(Document.id == document_id, Document.user_id == user_id)
    doc = (await db.execute(stmt)).scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    expires_at = (
        datetime.now(UTC) + timedelta(days=payload.expires_in_days)
        if payload.expires_in_days
        else None
    )

    share = DocumentShare(
        document_id=doc.id,
        recipient_email=payload.recipient_email,
        recipient_name=payload.recipient_name,
        expires_at=expires_at,
        download_allowed=payload.download_allowed,
        watermark_text=payload.watermark_text,
    )
    db.add(share)
    await db.commit()
    await db.refresh(share)

    viewer_url = f"{settings.app_base_url}/d/{share.share_token}"
    return {
        "share_id": share.id,
        "share_token": share.share_token,
        "viewer_url": viewer_url,
        "expires_at": share.expires_at.isoformat() if share.expires_at else None,
    }


@router.get("/api/v1/documents/{document_id}/analytics")
async def get_document_analytics(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Retrieves page-by-page duration and completion stats."""
    stmt = (
        select(Document)
        .where(Document.id == document_id, Document.user_id == user_id)
        .options(selectinload(Document.shares).selectinload(DocumentShare.events))
    )
    doc = (await db.execute(stmt)).scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Aggregate page duration across shares
    page_durations: dict[int, float] = {}
    total_views = 0
    for share in doc.shares:
        for ev in share.events:
            total_views += 1
            if ev.page_number is not None:
                page_durations[ev.page_number] = page_durations.get(ev.page_number, 0.0) + ev.duration_seconds

    page_stats = [
        {"page": p, "total_duration_seconds": round(dur, 1)}
        for p, dur in sorted(page_durations.items())
    ]

    return {
        "document_id": doc.id,
        "title": doc.title,
        "total_views": total_views,
        "page_analytics": page_stats,
    }


# Public Hosted Viewer Endpoints
@router.get("/d/{share_token}")
async def get_shared_document_metadata(
    share_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Public viewer endpoint providing document details for viewing."""
    stmt = (
        select(DocumentShare, Document)
        .join(Document, DocumentShare.document_id == Document.id)
        .where(DocumentShare.share_token == share_token, DocumentShare.is_active.is_(True))
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document share not found or expired.")

    share, doc = row
    if share.expires_at and share.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Document share has expired.")

    return {
        "title": doc.title,
        "total_pages": doc.total_pages,
        "download_allowed": share.download_allowed,
        "watermark": share.watermark_text,
        "recipient_email": share.recipient_email,
    }


@router.post("/d/{share_token}/event")
async def receive_buffered_document_events(
    share_token: str,
    payload: BufferedEventPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives buffered visibility and page duration logs from hosted PDF viewer.
    (PRD Requirement 26)
    """
    stmt = (
        select(DocumentShare, Document)
        .join(Document, DocumentShare.document_id == Document.id)
        .where(DocumentShare.share_token == share_token)
    )
    row = (await db.execute(stmt)).first()
    if not row:
        return {"status": "ignored"}

    share, doc = row
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    for ev in payload.events:
        doc_event = DocumentEvent(
            document_share_id=share.id,
            event_type=ev.event_type,
            page_number=ev.page_number,
            duration_seconds=ev.duration_seconds,
            ip_address=ip_addr,
            user_agent=user_agent,
        )
        db.add(doc_event)

    # Project document.opened/viewed to universal activity timeline
    await activity_bus.record_activity(
        session=db,
        user_id=doc.user_id,
        event_type="document.viewed",
        entity_type="document",
        entity_id=doc.id,
        source="pdf_viewer",
        metadata={
            "title": doc.title,
            "recipient_email": share.recipient_email,
            "events_count": len(payload.events),
        },
    )

    await db.commit()
    return {"status": "recorded", "count": len(payload.events)}
