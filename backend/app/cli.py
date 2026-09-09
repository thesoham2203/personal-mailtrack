"""CLI management and diagnostics tool (Doctor & Data Retention Cleanup)."""

import asyncio
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, text

from app.config import settings
from app.database import AsyncSessionLocal, engine, init_db
from app.models.documents import DocumentEvent
from app.models.events import ActivityEvent, ClickEvent, OpenEvent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


async def run_doctor():
    """Run diagnostics to verify local environment, database, and configurations."""
    print("==================================================")
    print("   PERSONAL MAILTRACK -- SYSTEM HEALTH DOCTOR     ")
    print("==================================================")
    all_ok = True

    # 1. Database Check
    print("\n[1/5] Checking Database...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                db_type = "SQLite" if "sqlite" in settings.database_url else "PostgreSQL"
                print(f"  [OK] Database connected successfully ({db_type})")
            else:
                print("  [FAIL] Database query failed.")
                all_ok = False
    except Exception as e:
        print(f"  [FAIL] Database connection error: {e}")
        all_ok = False

    # 2. Tracking Key Check
    print("\n[2/5] Checking Tracking Signing Keys...")
    key = settings.tracking_signing_key
    if key and len(key) >= 32 and not key.startswith("change-this"):
        print(f"  [OK] Tracking signing key configured ({len(key)} chars, secure)")
    elif key and len(key) >= 16:
        print(f"  [WARN] Tracking key present ({len(key)} chars), recommend 32+ random characters.")
    else:
        print("  [FAIL] Tracking signing key is missing or insecure! Set TRACKING_SIGNING_KEY in .env")
        all_ok = False

    # 3. Supabase Integration Check
    print("\n[3/5] Checking Supabase Credentials...")
    if settings.supabase_url and settings.supabase_anon_key:
        print(f"  [OK] Supabase URL configured: {settings.supabase_url}")
        print("  [OK] Supabase Anon Key configured")
    else:
        print("  [INFO] Supabase cloud credentials not set (running in standalone local mode).")

    # 4. Google OAuth Check
    print("\n[4/5] Checking Google OAuth Configuration...")
    if settings.google_client_id and settings.google_client_secret:
        print("  [OK] Google OAuth Client ID & Secret configured")
        print(f"  [OK] Redirect URI: {settings.google_redirect_uri}")
    else:
        print("  [INFO] Google OAuth credentials not set (Gmail API reply sync disabled until set).")

    # 5. Base URLs Check
    print("\n[5/5] Checking Base URLs (Domain Agnostic)...")
    print(f"  [OK] API Base URL:      {settings.api_base_url}")
    print(f"  [OK] Tracking Base URL: {settings.tracking_base_url}")
    print(f"  [OK] App Base URL:      {settings.app_base_url}")

    print("\n--------------------------------------------------")
    if all_ok:
        print("RESULT: ALL CORE SYSTEMS HEALTHY AND OPERATIONAL! [OK]")
    else:
        print("RESULT: ISSUES DETECTED. PLEASE REVIEW THE WARNINGS ABOVE. [FAIL]")
    print("==================================================\n")
    return all_ok


async def run_cleanup():
    """Clean up tracking events older than EVENT_RETENTION_DAYS."""
    days = settings.event_retention_days
    cutoff = datetime.now(UTC) - timedelta(days=days)
    print(f"Running data retention cleanup for events older than {days} days ({cutoff.isoformat()})...")

    async with AsyncSessionLocal() as session:
        # Delete old open events
        res_open = await session.execute(
            delete(OpenEvent).where(OpenEvent.occurred_at < cutoff)
        )
        # Delete old click events
        res_click = await session.execute(
            delete(ClickEvent).where(ClickEvent.occurred_at < cutoff)
        )
        # Delete old doc events
        res_doc = await session.execute(
            delete(DocumentEvent).where(DocumentEvent.occurred_at < cutoff)
        )
        # Delete old activity events
        res_act = await session.execute(
            delete(ActivityEvent).where(ActivityEvent.occurred_at < cutoff)
        )
        await session.commit()

        print(f"Deleted {res_open.rowcount} open events, {res_click.rowcount} click events, "
              f"{res_doc.rowcount} document events, {res_act.rowcount} activity events.")
        print("Cleanup completed successfully.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "doctor":
        asyncio.run(run_doctor())
    elif len(sys.argv) > 1 and sys.argv[1] == "initdb":
        print("Initializing database tables...")
        asyncio.run(init_db())
        print("Tables initialized successfully.")
    elif len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        asyncio.run(run_cleanup())
    elif len(sys.argv) > 1 and sys.argv[1] == "seed":
        from app.services.demo.generator import seed_demo_data
        from app.routers.emails import get_current_user_id

        async def run_seed():
            async with AsyncSessionLocal() as session:
                user_id = await get_current_user_id(session)
                res = await seed_demo_data(session, user_id)
                print(f"Demo data seeded successfully: {res}")

        print("Seeding demo contacts, tracked emails, and document activity...")
        asyncio.run(run_seed())
    else:
        print("Usage: python -m app.cli [doctor|initdb|cleanup|seed]")


if __name__ == "__main__":
    main()
