"""API Router for System Health and Setup Doctor UI."""

from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import engine

router = APIRouter(prefix="/api/v1/diagnostics", tags=["Diagnostics"])


@router.get("/doctor")
async def get_doctor_diagnostics():
    """Returns system status for the Setup Doctor screen."""
    # 1. Database Check
    db_ok = False
    db_error = None
    try:
        async with engine.connect() as conn:
            val = (await conn.execute(text("SELECT 1"))).scalar()
            db_ok = (val == 1)
    except Exception as e:
        db_error = str(e)

    # 2. Tracking Key Check
    key = settings.tracking_signing_key
    key_ok = bool(key and len(key) >= 16 and not key.startswith("change-this"))

    # 3. Supabase Integration
    supabase_ok = bool(settings.supabase_url and settings.supabase_anon_key)

    # 4. Google OAuth
    oauth_ok = bool(settings.google_client_id and settings.google_client_secret)

    return {
        "overall_healthy": db_ok and key_ok,
        "checks": {
            "database": {
                "status": "connected" if db_ok else "error",
                "type": "sqlite" if "sqlite" in settings.database_url else "postgresql",
                "error": db_error,
                "label": "Database Engine",
            },
            "tracking_key": {
                "status": "configured" if key_ok else "warning",
                "length": len(key) if key else 0,
                "label": "Cryptographic Tracking Keys",
            },
            "supabase": {
                "status": "configured" if supabase_ok else "local_mode",
                "url": settings.supabase_url if supabase_ok else None,
                "label": "Supabase Platform Core",
            },
            "google_oauth": {
                "status": "configured" if oauth_ok else "not_configured",
                "label": "Google OAuth (Gmail Sync)",
            },
        },
        "base_urls": {
            "api": settings.api_base_url,
            "tracking": settings.tracking_base_url,
            "app": settings.app_base_url,
        },
        "features": {
            "campaigns": settings.feature_campaigns,
            "documents": settings.feature_documents,
            "signatures": settings.feature_signatures,
            "polls": settings.feature_polls,
            "video": settings.feature_video,
            "webhooks": settings.feature_webhooks,
        },
    }
