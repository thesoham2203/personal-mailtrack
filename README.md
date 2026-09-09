# Personal Mailtrack / Mailsuite-Style Email Productivity Suite

A clean-room, personal-use Gmail email tracking, productivity, and analytics system inspired by the premium feature set of Mailtrack/Mailsuite.

Built from the ground up with **Python 3.12+ / FastAPI**, **Supabase / PostgreSQL & Async SQLite**, **Chromium Manifest V3 (Brave Desktop + Gmail Web)**, and **React 18 + TypeScript + Tailwind CSS**.

---

## Table of Contents

- [Key Principles](#key-principles)
- [Architecture & System Flow](#architecture--system-flow)
- [Feature Deep-Dive](#feature-deep-dive)
  - [1. Real-Time Email & Open Tracking](#1-real-time-email--open-tracking)
  - [2. Safe Link Click Tracking](#2-safe-link-click-tracking)
  - [3. Chromium Manifest V3 Extension (Brave + Gmail Web)](#3-chromium-manifest-v3-extension-brave--gmail-web)
  - [4. Follow-Up Intelligence & Productivity Command Center](#4-follow-up-intelligence--productivity-command-center)
  - [5. Lightweight CRM & Heuristic Engagement Scoring](#5-lightweight-crm--heuristic-engagement-scoring)
  - [6. Personalized Campaigns & Mail Merge](#6-personalized-campaigns--mail-merge)
  - [7. PDF & Document Tracking with Hosted Viewer](#7-pdf--document-tracking-with-hosted-viewer)
  - [8. Automations & Outbound Webhooks](#8-automations--outbound-webhooks)
  - [9. Privacy, Security & Data Retention](#9-privacy-security--data-retention)
- [Project Directory Structure](#project-directory-structure)
- [Step-by-Step Setup & Run Guide](#step-by-step-setup--run-guide)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Extension Setup (Brave Desktop)](#2-extension-setup-brave-desktop)
  - [3. Dashboard Setup](#3-dashboard-setup)
- [Configuration Reference (`.env`)](#configuration-reference-env)
- [API Surface Reference](#api-surface-reference)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Supabase & Cloud Deployment](#supabase--cloud-deployment)
- [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)
- [License & Clean-Room Disclaimer](#license--clean-room-disclaimer)

---

## Key Principles

- **Personal-First & Single-User**: Designed specifically for individual productivity and freelancers. Zero SaaS overhead—no multi-tenant billing, team administration, or complex enterprise SSO.
- **Free-Tier-First**: Operates seamlessly on free managed tiers. Uses asynchronous background tasks and persistent database tables instead of heavy message brokers (no Redis, Celery, or Kafka required).
- **Domain-Agnostic Core**: Initial deployment runs without owning a custom domain (`http://localhost:8000` or temporary cloud hostnames). Migrates to custom domains (`track.example.com`, `api.example.com`) purely via configuration without code changes.
- **Fail-Open Send Guarantee**: Send interception enforces a strict `TRACKING_PREPARE_TIMEOUT_MS` (default 2500ms). If the tracking server is offline or delayed, it catches the timeout and fires the native send immediately. **Normal Gmail sending is never blocked.**
- **Dual-Database Mode**: Run out-of-the-box on **Async SQLite** without any cloud accounts or credentials. Switch to **Supabase PostgreSQL** in production by updating `.env` with identical business logic.
- **Bot & Scanner Intelligence**: Retains all raw activity events while classifying requests via `EventClassifier` (`human_likely`, `proxy_likely`, `security_scanner_likely`, `automation_likely`) so you always know when a real human engaged.

---

## Architecture & System Flow

```
+-------------------------------------------------------------------------------+
|                                Brave Desktop                                  |
|                                                                               |
|   +------------------------------------+   +-------------------------------+  |
|   |             Gmail Web              |   |       React Dashboard         |  |
|   |  - Compose Toolbar Toggle (✓✓)     |   |  - Live Activity Feed         |  |
|   |  - Fail-Open Send Interceptor      |   |  - Follow-up Command Center   |  |
|   |  - Sent Folder Checkmark Badges    |   |  - Contacts CRM & Scoring     |  |
|   |  - In-Browser Debugger (Ctrl+Sh+D) |   |  - Campaigns & Mail Merge     |  |
|   +-----------------+------------------+   |  - PDF Viewer & Dwell Time    |  |
|                     |                      +---------------+---------------+  |
|   +-----------------v------------------+                   |                  |
|   |  Manifest V3 Background Service    |                   |                  |
|   |  - Chrome Alarms Periodic Sync     |                   |                  |
|   |  - Desktop Notification Dispatch   |                   |                  |
|   +-----------------+------------------+                   |                  |
+---------------------|--------------------------------------|------------------+
                      | REST API / Pixels / Redirects        |
                      v                                      v
+-------------------------------------------------------------------------------+
|                           FastAPI Backend (/backend)                          |
|                                                                               |
|  +---------------------+  +----------------------+  +----------------------+  |
|  |   Tracking Engine   |  |   Follow-up Engine   |  |   Campaign Engine    |  |
|  | - HMAC Capabilities |  | - Hot Conversations  |  | - Safe Merge Renderer|  |
|  | - 1x1 GIF Ingress   |  | - Revival Alerts     |  | - Suppression Filter |  |
|  | - SSRF URL Safety   |  | - Waiting-on-Them/Me |  | - Rate-Limit State   |  |
|  | - Bot Classifier    |  | - No-Reply Timers    |  |                      |  |
|  +----------+----------+  +----------+-----------+  +----------+-----------+  |
|             |                        |                         |              |
|             +------------------------+-------------------------+              |
|                                      |                                        |
|                         +------------v-------------+                          |
|                         |   Universal Activity Bus |                          |
|                         |   (activity_events)      |                          |
|                         +------------+-------------+                          |
+--------------------------------------|----------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
      +-------------------------+             +-------------------------+
      |      Async SQLite       |             |   Supabase PostgreSQL   |
      |   (Local Zero-Config)   |             |    (Cloud Production)   |
      |     ./mailtrack.db      |             |   RLS + Storage + RT    |
      +-------------------------+             +-------------------------+
```

---

## Feature Deep-Dive

### 1. Real-Time Email & Open Tracking
- **Ultra-Lightweight Pixel (`GET /t/o/{token}`)**: Fast pixel endpoint verifying in-memory HMAC-SHA256 tokens before database writes. Returns a 1x1 transparent GIF with aggressive cache-busting headers (`Cache-Control: no-store, no-cache, must-revalidate, max-age=0`).
- **Fail-Silent Security**: Tampered, expired, or invalid tokens return a valid 200 transparent GIF without logging errors or leaking server internals.
- **Bot & Proxy Classifier (`EventClassifier`)**: Evaluates request latency after send, user-agent signatures, header fingerprints (Accept, Range, Pragma), and known image proxies (GoogleImageProxy, Yahoo, Outlook). Distinguishes raw hits from verified human opens.

### 2. Safe Link Click Tracking
- **Cryptographically Bound Redirects (`GET /t/c/{token}?u=...`)**: Cryptographically binds the recipient capability token to the destination URL using constant-time `hmac.compare_digest`.
- **Strict SSRF URL Safety**: Rejects dangerous schemes (`javascript:`, `data:`, `file:`, `vbscript:`), protocol-relative URLs (`//`), user credentials (`user:pass@`), loopback addresses (`127.0.0.1`, `::1`), private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and link-local ranges.
- **Universal Event Projection**: Click events automatically log to `click_events` and project onto the universal `activity_events` timeline.

### 3. Chromium Manifest V3 Extension (Brave + Gmail Web)
- **Native Gmail Integration**: Injects a clean `✓✓ Tracked` toggle button directly into the Gmail Compose toolbar and dynamic status badges into the Sent folder (`✓` Tracked, `✓✓` Opened, `↗` Clicked, `↩` Replied, `🔥` Hot).
- **Double-Send Prevention**: Uses an atomic `activeSends` guard to guarantee sending is never triggered twice.
- **Fail-Open Send Guard**: Enforces `TRACKING_PREPARE_TIMEOUT_MS` (default 2500ms). If tracking preparation times out or fails, the email sends normally through Gmail.
- **In-Browser Diagnostics Overlay**: Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd> inside Gmail to launch the **Mailtrack Debugger** modal to inspect selector match counts, Brave detection status, backend reachability, and active send states.
- **Manifest V3 Safe Alarms**: Background reconciliation uses `chrome.alarms` (1-minute interval) rather than `setInterval` to prevent drops when the service worker is idle.
- **Desktop Notifications**: Automatic desktop alerts on open and click events with an in-memory deduplication set to avoid notification spam.

### 4. Follow-Up Intelligence & Productivity Command Center
- **Hot Conversations**: Automatically surfaces threads receiving 3+ likely-human opens within 30 minutes.
- **Waiting on Them**: Identifies sent emails that haven't received replies, sorted by age and engagement.
- **Waiting on Me**: Stubs and prepares incoming threads where the recipient replied and you need to answer.
- **No-Reply Overdue**: Configurable 24h / 48h / 72h reminder thresholds.
- **Revival Alerts**: Alerts you when a dormant email (idle for 7+ days) is suddenly reopened.

### 5. Lightweight CRM & Heuristic Engagement Scoring
- **Automatic Contact Upsert**: Automatically creates and links contacts upon sending or receiving emails.
- **Heuristic Activity Score**:
  - Open: `+1` | Reopen: `+2` | Link Click: `+5` | PDF View: `+5` | Reply: `+20` | Bounce: `-50` | Unsubscribe: `-100`
- **Dynamic Classification**: Automatically categorizes contacts into **Hot** (score ≥ 30), **Warm** (score ≥ 10), or **Cold** (score < 10).
- **Unified Interaction Timeline**: Complete chronological history of all interactions with each contact.

### 6. Personalized Campaigns & Mail Merge
- **Safe Template Engine**: Regex-based safe variable interpolation supporting fallback defaults (e.g. `{{first_name | fallback: "there"}}`, `{{company}}`). Never executes arbitrary or untrusted code.
- **Individualized Tracking Identity**: Every campaign recipient receives a distinct pixel, individual tracking links, and a secure unsubscribe capability token (`GET /u/{token}`).
- **Suppression Enforcement**: Automatically verifies contacts against bounce and unsubscribe lists before sending.

### 7. PDF & Document Tracking with Hosted Viewer
- **Secure Hosted Viewer**: Built with PDF.js to load documents via capability tokens without making private files public.
- **Buffered Dwell Analytics**: Client-side session buffer records page-by-page duration and flushes data on page transitions, visibility changes, and window close using `navigator.sendBeacon`.
- **Dynamic Confidentiality Watermark**: Generates dynamic watermarks on derived views (e.g., `CONFIDENTIAL - recipient@example.com - YYYY-MM-DD`).

### 8. Automations & Outbound Webhooks
- **WHEN / IF / THEN Rule Engine**: Evaluates automation rules on any event arriving on the `activity_events` bus.
- **Outbound Webhooks**: Dispatches HMAC-signed POST webhooks to external URLs with SSRF validation.

### 9. Privacy, Security & Data Retention
- **Privacy Mode**: IP anonymization and coarse location options.
- **Data Retention & CLI Cleanup**: Automated cleanup of expired tracking events (`python -m app.cli cleanup`).
- **Cryptographic Separation**: Public tokens contain only cryptographic capability signatures; internal sequential database IDs are never exposed.

---

## Project Directory Structure

```
personal-mailtrack/
├── backend/                           # FastAPI Python Backend
│   ├── app/
│   │   ├── auth/                      # Personal Auth & Header Dependencies
│   │   │   ├── __init__.py
│   │   │   └── dependencies.py        # Header-based EXTENSION_API_KEY validator
│   │   ├── config.py                  # Pydantic Settings & Environment Variables
│   │   ├── database.py                # Dual SQLite / PostgreSQL Async Engine
│   │   ├── cli.py                     # CLI Tools: doctor, initdb, cleanup, seed
│   │   ├── main.py                    # FastAPI App Definition & Router Mounting
│   │   ├── models/                    # SQLAlchemy 2.0 Async Data Models
│   │   │   ├── profiles.py            # Profiles, Gmail Accounts, OAuth Credentials
│   │   │   ├── tracked_emails.py      # Tracked Emails, Recipients, Links
│   │   │   ├── events.py              # Open, Click, Reply, Bounce & Activity Events
│   │   │   ├── contacts.py            # Contacts, Contact Lists, Notes
│   │   │   ├── campaigns.py           # Campaigns, Campaign Recipients, Events
│   │   │   ├── documents.py           # Documents, Document Shares, Document Events
│   │   │   ├── automations.py         # Automation Rules, Webhooks & Deliveries
│   │   │   └── notifications.py       # Notification Rules & Delivery Events
│   │   ├── routers/                   # REST API Routers (/api/v1 & Public)
│   │   │   ├── auth.py                # GET /me, Account Info
│   │   │   ├── gmail.py               # Gmail Status, OAuth URL, Accounts, Sync
│   │   │   ├── followup.py            # Hot, Revival, Waiting-on-Them, No-Reply
│   │   │   ├── tracking.py            # /t/o/{token}, /t/c/{token}, /u/{token}
│   │   │   ├── emails.py              # Email Registration, Logs, Timeline
│   │   │   ├── contacts.py            # Contacts CRUD, CRM Timeline
│   │   │   ├── campaigns.py           # Campaign CRUD, Preview, Send Controls
│   │   │   ├── templates.py           # Email Templates CRUD
│   │   │   ├── documents.py           # PDF Upload, Shares (/d/{token}), Events
│   │   │   ├── analytics.py           # Aggregated Metrics, Activity Feeds
│   │   │   ├── notifications.py       # Notification Rules Management
│   │   │   ├── automations.py         # Automation Rules CRUD
│   │   │   ├── webhooks.py            # Outbound Webhook Destinations
│   │   │   └── diagnostics.py         # Diagnostic Health Endpoint
│   │   ├── security/                  # Cryptography & Validation
│   │   │   ├── tracking_tokens.py     # HMAC-SHA256 Capability Tokens
│   │   │   ├── url_safety.py          # Strict SSRF & Destination Safety Filter
│   │   │   └── encryption.py          # AES-GCM / Fernet Token Encryption
│   │   └── services/                  # Business Logic Layer
│   │       ├── tracking/              # Ingress Pixel Engine & EventClassifier
│   │       ├── events/                # Universal ActivityBus Projector
│   │       ├── followup/              # Hot / Revival / Waiting-on-Them Manager
│   │       ├── gmail/                 # Credential-Gated OAuth & Sync Stubs
│   │       ├── contacts/              # CRM Upsert & Engagement Scoring
│   │       ├── campaigns/             # Safe Mail-Merge & Suppression Engine
│   │       ├── documents/             # Share Access & Expiry Manager
│   │       ├── automation/            # WHEN/IF/THEN Rule Evaluator
│   │       └── demo/                  # Synthetic Demo Data Generator
│   ├── supabase/
│   │   └── schema.sql                 # Production PostgreSQL DDL, Indexes & RLS
│   ├── tests/                         # 28 Unit & Integration Pytest Suite
│   │   ├── unit/                      # Tokens, URL safety, classifier, merge
│   │   └── integration/               # Tracking flow, fail-open, followup
│   ├── pyproject.toml                 # Backend Dependencies & Tool Config
│   └── .env.example                   # Sample Environment Variables
├── extension/                         # Chromium Manifest V3 Extension
│   ├── manifest.json                  # Extension Manifest (storage, notifications, alarms)
│   ├── background/                    # Background Service Worker & Helpers
│   │   ├── service-worker.ts          # Main Service Worker & Alarms Listener
│   │   ├── api-client.ts              # Typed Backend Fetch Wrapper
│   │   ├── auth.ts                    # Local Storage Credential & Session Store
│   │   ├── sync.ts                    # Chrome Alarms Periodic Sync Engine
│   │   └── notifications.ts           # Desktop Notification Dispatch with Dedup
│   ├── content/                       # Content Scripts Injected into Gmail
│   │   ├── selectors.ts               # Centralized Gmail DOM Selectors & Metrics
│   │   ├── injector.ts                # Fail-Open Send Interceptor & Double-Send Guard
│   │   ├── compose.ts                 # Native Compose Toolbar Toggle Button
│   │   ├── sent.ts                    # Sent Message List Badges (✓, ✓✓, ↗, ↩, 🔥)
│   │   ├── debugger.ts                # In-Browser Diagnostics Modal (Ctrl+Shift+D)
│   │   └── content.ts                 # Content Script Entry Point
│   ├── popup/                         # Extension Popup (Quick Activity Feed)
│   ├── options/                       # Extension Settings Page (Base URLs, Timeout)
│   ├── shared/                        # Shared Types, Storage Wrapper, Constants
│   ├── build.js                       # Esbuild Bundling Script
│   └── package.json
└── dashboard/                         # React 18 + TypeScript + Vite Dashboard
    ├── src/
    │   ├── pages/                     # 9 Complete Application Views
    │   │   ├── ActivityPage.tsx       # Live Activity Stream with Bot Filters
    │   │   ├── EmailsPage.tsx         # Tracked Emails List & Certificate Modal
    │   │   ├── FollowUpPage.tsx       # Hot, Waiting-on-Them, No-Reply, Revived
    │   │   ├── ContactsPage.tsx       # CRM Scoring & Contact Timeline Drawer
    │   │   ├── CampaignsPage.tsx      # Mail Merge Wizard & Recipient Stats
    │   │   ├── DocumentsPage.tsx      # PDF Upload & Reader Dwell Analytics
    │   │   ├── TemplatesPage.tsx      # Reusable Email Templates Manager
    │   │   ├── ReportsPage.tsx        # Productivity & Interaction Metrics
    │   │   └── SetupDoctorPage.tsx    # Diagnostic Self-Test & System Health
    │   ├── viewer/                    # Hosted PDF Document Viewer
    │   │   └── DocumentViewer.tsx     # PDF.js Viewer with Buffered Beacon
    │   ├── services/api.ts            # Typed Backend API Client
    │   ├── App.tsx                    # Main App Shell & Navigation
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

---

## Step-by-Step Setup & Run Guide

### Prerequisites

- **Python 3.12+** (recommended: [uv](https://github.com/astral-sh/uv) or standard `python`)
- **Node.js 18+** & **npm**
- **Brave Desktop Browser** (or any Chromium browser such as Chrome or Edge)

---

### 1. Backend Setup

Open a terminal in `d:\personal-mailtrack\backend`:

```powershell
# Navigate to backend folder
cd d:\personal-mailtrack\backend

# Option A: Using uv (fastest)
uv venv .venv
.\.venv\Scripts\activate
uv pip install -e ".[dev]"

# Option B: Using standard Python venv & pip
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Initialize the database and verify system health:

```powershell
# Copy environment configuration
Copy-Item .env.example .env

# Initialize database schema (creates local SQLite mailtrack.db)
python -m app.cli initdb

# Run the Doctor CLI to verify configuration and keys
python -m app.cli doctor

# Seed rich demo data (contacts, tracked emails, opens, clicks, documents)
python -m app.cli seed
```

Start the FastAPI development server:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

- **Interactive Swagger Docs**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **Health Check**: [`http://localhost:8000/health`](http://localhost:8000/health)

---

### 2. Extension Setup (Brave Desktop)

Open a second terminal in `d:\personal-mailtrack\extension`:

```powershell
cd d:\personal-mailtrack\extension

# Install build dependencies
npm install

# Compile TypeScript into the unpacked distribution (/dist)
npm run build
```

**Load the extension into Brave:**

1. Open Brave and navigate to `brave://extensions` (or `chrome://extensions`).
2. Toggle on **Developer mode** in the top right corner.
3. Click the **Load unpacked** button.
4. Select the `d:\personal-mailtrack\extension\dist` directory.
5. Open [Gmail Web](https://mail.google.com):
   - Open a **Compose** window: Notice the green `✓✓ Tracked` toggle button in the toolbar.
   - Look at your **Sent** folder: Badges (`✓`, `✓✓`, `↗`, `↩`, `🔥`) appear next to tracked messages with interactive tooltips.
   - Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd> anywhere on Gmail to open the **Mailtrack Debugger** overlay.

---

### 3. Dashboard Setup

Open a third terminal in `d:\personal-mailtrack\dashboard`:

```powershell
cd d:\personal-mailtrack\dashboard

# Install dashboard dependencies
npm install

# Start Vite development server
npm run dev
```

Open [`http://localhost:5173`](http://localhost:5173) in Brave to explore:
- **Activity**: Live feed of opens, clicks, and document views with human vs bot filtering.
- **Emails**: Searchable email log with Delivery Certificate modal.
- **Follow-up**: Priority queues for Hot conversations, Waiting on them, and No-reply overdue.
- **Contacts**: CRM scores with interactive contact history timeline.
- **Campaigns**: Mail-merge wizard with individualized preview.
- **Documents**: PDF upload and page-by-page reader dwell duration charts.
- **Setup Doctor**: Real-time diagnostic self-test.

---

## Configuration Reference (`.env`)

Configure settings in `backend/.env`:

| Variable | Default Value | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment mode (`development`, `staging`, `production`). |
| `API_BASE_URL` | `http://localhost:8000` | Base URL used by the extension & dashboard to hit the API. |
| `TRACKING_BASE_URL` | `http://localhost:8000` | Base URL embedded in pixels & link redirects (supports future custom domains). |
| `APP_BASE_URL` | `http://localhost:5173` | Base URL for the dashboard and hosted document viewer. |
| `DATABASE_URL` | `sqlite+aiosqlite:///./mailtrack.db` | SQLAlchemy async connection string (SQLite for local, PostgreSQL for cloud). |
| `TRACKING_SIGNING_KEY` | *(Auto-generated 42-char key)* | Secret key for signing HMAC capability tokens. |
| `TRACKING_PREVIOUS_KEYS` | `[]` | List of previous keys to support zero-downtime key rotation. |
| `ENCRYPTION_KEY` | *(Auto-generated 32-byte key)* | Secret key for AES-GCM / Fernet token encryption at rest. |
| `TRACKING_PREPARE_TIMEOUT_MS` | `2500` | Max milliseconds extension waits before failing open and sending normally. |
| `PRIVACY_MODE` | `true` | When true, anonymizes client IP addresses and suppresses granular geo-tracking. |
| `EVENT_RETENTION_DAYS` | `90` | Days to retain raw event logs before CLI cleanup. |
| `EXTENSION_API_KEY` | `""` | Optional static key required in `X-API-Key` header for personal protection. |
| `PERSONAL_USER_ID` | `00000000-0000-0000-0000-000000000001` | Default single-user ownership UUID. |
| `GOOGLE_CLIENT_ID` | `""` | Optional Google OAuth Client ID for Gmail API reply sync. |
| `GOOGLE_CLIENT_SECRET` | `""` | Optional Google OAuth Client Secret for Gmail API reply sync. |
| `GOOGLE_REDIRECT_URI` | `""` | OAuth callback redirect URL. |
| `SUPABASE_URL` | `""` | Optional Supabase cloud project URL. |
| `SUPABASE_ANON_KEY` | `""` | Optional Supabase public anon key. |
| `SUPABASE_SERVICE_ROLE_KEY` | `""` | Optional Supabase service role key (**server-side only**). |

---

## API Surface Reference

All core endpoints are versioned under `/api/v1` (with high-speed public tracking routes mounted at root):

### Public High-Speed Tracking Endpoints
- `GET /t/o/{token}` — Returns 1x1 transparent GIF pixel, verifies HMAC, and logs open event.
- `GET /t/c/{token}?u={url}` — Cryptographically verifies destination URL, logs click, and issues 302 redirect.
- `GET /u/{token}` — Unsubscribe capability link for campaign recipients (updates suppression list).
- `GET /d/{share_token}` — Public document viewer redirect for tracked PDFs.
- `POST /d/{share_token}/event` — Receives buffered dwell time beacon from the hosted document viewer.

### Application API (`/api/v1`)
- `GET /api/v1/health` — System status, database health, and configuration state.
- `GET /api/v1/me` — Current personal user profile and Gmail integration status.
- `POST /api/v1/emails` — Intercept endpoint: registers email, generates signed tracking pixel & rewritten links.
- `GET /api/v1/emails` & `GET /api/v1/emails/{id}` — Tracked email logs and full interaction timeline.
- `GET /api/v1/followup/hot` — Hot conversations receiving 3+ opens within 30 minutes.
- `GET /api/v1/followup/revival` — Dormant emails (7+ days idle) recently reopened.
- `GET /api/v1/followup/waiting-on-them` — Unreplied sent messages awaiting response.
- `GET /api/v1/followup/no-reply` — Configurable no-reply overdue threshold monitor.
- `GET /api/v1/contacts` & `POST /api/v1/contacts` — Contacts CRM and engagement score history.
- `GET /api/v1/campaigns` & `POST /api/v1/campaigns` — Mail-merge campaigns with preview and dispatch state machine.
- `GET /api/v1/templates` & `POST /api/v1/templates` — Reusable email templates.
- `GET /api/v1/documents` & `POST /api/v1/documents` — PDF upload, share link creation, and page duration logs.
- `GET /api/v1/analytics/summary` — Aggregate metrics (sent, opens, clicks, replies, document views).
- `GET /api/v1/notifications/rules` — Notification rules configuration.
- `GET /api/v1/automations` & `POST /api/v1/automations` — Automation rule engine triggers.
- `GET /api/v1/webhooks` & `POST /api/v1/webhooks` — Outbound SSRF-validated webhook subscriptions.
- `GET /api/v1/diagnostics/doctor` — Setup doctor test suite results.

---

## Testing & Quality Assurance

The codebase includes an automated test suite covering unit logic, integration lifecycles, cryptographic security, and fail-open guarantees:

```powershell
cd d:\personal-mailtrack\backend

# Run all 28 pytest tests with verbose output
.\.venv\Scripts\python -m pytest tests/ -v
```

### Test Coverage Highlights
- **Tracking Tokens (`test_tracking_tokens.py`)**: Token generation, round-trip HMAC verification, tampered token rejection, malformed string protection, click URL binding, and key rotation.
- **SSRF & URL Safety (`test_url_safety.py`)**: Public URL allowance, dangerous scheme rejection (`javascript:`, `data:`, `file:`), loopback & private IP blocking (`127.0.0.1`, `10.x`, `172.16.x`, `192.168.x`, `::1`), and userinfo stripping.
- **Bot Classifier (`test_bot_classifier.py`)**: Image proxy detection (GoogleImageProxy, Yahoo, Outlook), instant scanner detection (< 1.5s after send), and interactive human open validation.
- **Mail Merge Engine (`test_campaign_merge.py`)**: Variable replacement, fallback defaults, multiple variables, missing variable safety, and case-insensitive bounce/unsubscribe suppression.
- **Fail-Open Guarantee (`test_fail_open.py`)**: Simulates server delay and timeout, verifying send interception aborts gracefully and allows native sending.
- **Full Tracking Lifecycle (`test_tracking_flow.py`)**: End-to-end simulation from email registration to 1x1 GIF pixel request, click redirect, and universal `activity_events` projection.

### Linting & Static Analysis
```powershell
cd d:\personal-mailtrack\backend
.\.venv\Scripts\python -m ruff check app/ tests/
```

---

## Supabase & Cloud Deployment

To transition from local SQLite to Supabase PostgreSQL:

1. Create a free project at [supabase.com](https://supabase.com).
2. Navigate to the **SQL Editor** in your Supabase project dashboard.
3. Open `backend/supabase/schema.sql`, copy the contents, and run it. This creates all tables, performance indexes, and Row Level Security (RLS) policies.
4. Update `backend/.env` with your Supabase credentials:
   ```dotenv
   DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
   SUPABASE_URL=https://[YOUR-PROJECT].supabase.co
   SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
   SUPABASE_SERVICE_ROLE_KEY=[YOUR-SERVICE-ROLE-KEY]
   ```
5. Verify cloud connectivity:
   ```powershell
   python -m app.cli doctor
   ```

### Deploying the Backend & Dashboard
- **Backend**: Can be hosted on any free/low-cost Python hosting provider (Render, Railway, Fly.io, or your own VPS).
- **Dashboard**: Can be deployed to Vercel, Netlify, or Cloudflare Pages as a static SPA.
- **Custom Domain Migration**: When ready to add a custom domain (e.g. `track.yourdomain.com`), simply point a CNAME to your hosted backend and update `TRACKING_BASE_URL` in `.env`.

---

## Troubleshooting & Diagnostics

### 1. In-Browser Mailtrack Debugger
Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd> inside Gmail at any time. The diagnostics overlay will display:
- Environment validation (Brave Desktop / Chromium detection)
- Gmail DOM selector match status (compose dialog, send button, message rows)
- Backend API reachability & latency
- Active send interception state

### 2. CLI Doctor
Run the CLI doctor whenever troubleshooting local setup:
```powershell
cd backend
python -m app.cli doctor
```

### 3. Data Retention Cleanup
Purge tracking events older than your configured retention window (`EVENT_RETENTION_DAYS`):
```powershell
cd backend
python -m app.cli cleanup
```

### 4. Common Tips
- **Brave Shields / Ad Blockers**: When testing locally, ensure Brave Shields or ad-blocking extensions do not block requests to `localhost:8000` (which hosts tracking pixels).
- **Gmail DOM Updates**: If Gmail updates its interface, update selectors in `extension/content/selectors.ts`—all DOM selectors are centralized in a single dictionary with fallback chains.

---

## License & Clean-Room Disclaimer

This project is an original clean-room implementation built for personal productivity. It does not contain proprietary source code, copyrighted assets, or private APIs from Mailtrack, Mailsuite, or their parent companies.

Released under the **MIT License**.
