# Personal Mailtrack / Mailsuite-Style Email Productivity Suite

Clean-room personal email tracking, analytics, and productivity system built with **FastAPI**, **Supabase / SQLite**, **Chromium Manifest V3 (Brave Desktop + Gmail Web)**, and **React + TypeScript**.

Free-tier-first, single-user, domain-agnostic.

---

## Architecture Overview

- **Backend (`/backend`)**: FastAPI (Python 3.12+), SQLAlchemy 2.0 Async, Pydantic v2. Dual-mode database (Async SQLite for zero-friction local development, Supabase PostgreSQL for cloud deployment).
- **Tracking Core**: In-memory HMAC-SHA256 capability tokens with key rotation, strict SSRF/destination URL validation, `EventClassifier` for image proxy/bot detection, and universal `activity_events` chronological timeline.
- **Gmail Extension (`/extension`)**: Chromium Manifest V3 designed for **Brave Desktop** and **Gmail Web**. Minimal permissions (no `declarativeNetRequest`, no `<all_urls>`). Native compose integration with fail-open send guarantee (configurable `TRACKING_PREPARE_TIMEOUT_MS`, default 2500ms), double-send prevention, checkmark indicators (`✓`, `✓✓`, `↗`, `↩`, `🔥`), and in-browser `Mailtrack Debugger` (Ctrl+Shift+D).
- **Web Dashboard (`/dashboard`)**: React 18, TypeScript, Tailwind CSS, Vite. Live activity feed, filterable emails list, Follow-up inbox (Hot, Waiting on them, No-reply overdue, Revived), Contacts CRM with heuristic engagement scores, Mail-merge campaigns with personalization preview, Document/PDF tracker, and Setup Doctor.
- **Hosted Document Viewer**: PDF.js viewer with client-side session buffer reporting page-by-page duration analytics via `navigator.sendBeacon` and dynamic confidentiality watermarking.

---

## Quick Start (Local Run)

### 1. Backend

```powershell
cd backend
# Create virtual environment and install dependencies
uv venv .venv
.\.venv\Scripts\activate
uv pip install -e ".[dev]"

# Initialize database and run health doctor
python -m app.cli initdb
python -m app.cli doctor

# Optional: Seed realistic demo data for immediate exploration
python -m app.cli seed

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

The API will run at `http://localhost:8000`. Test `/health` or open the interactive API documentation at `http://localhost:8000/docs`.

### 2. Chromium Extension (Brave Desktop)

```powershell
cd extension
npm install
npm run build
```

1. Open Brave Desktop and navigate to `brave://extensions` (or `chrome://extensions`).
2. Toggle **Developer mode** in the top right.
3. Click **Load unpacked** and select the `d:\personal-mailtrack\extension\dist` directory.
4. Open [Gmail Web](https://mail.google.com).
5. Click **Compose**: you will see the `✓✓ Tracked` toggle button in the compose toolbar.
6. Press **Ctrl+Shift+D** anytime to open the **Mailtrack Debugger** overlay.

### 3. Web Dashboard

```powershell
cd dashboard
npm install
npm run dev
```

Open `http://localhost:5173` to view the live dashboard.

---

## Test Suite

Run the automated test suite with pytest:

```powershell
cd backend
python -m pytest tests/ -v
```

Run code style & lint check:

```powershell
python -m ruff check app/ tests/
```

---

## Production Supabase PostgreSQL Deployment

1. Create a free project on [Supabase](https://supabase.com).
2. Run the SQL schema in `backend/supabase/schema.sql` inside the Supabase SQL Editor.
3. In `backend/.env`:
   ```dotenv
   DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT].supabase.co:5432/postgres
   SUPABASE_URL=https://[YOUR-PROJECT].supabase.co
   SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
   SUPABASE_SERVICE_ROLE_KEY=[YOUR-SERVICE-ROLE-KEY]
   ```
4. Run `python -m app.cli doctor` to verify Supabase connectivity.
