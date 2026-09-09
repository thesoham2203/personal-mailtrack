# Deployment Guide — Personal Mailtrack

> ⚠️ This file is in `.gitignore` — it will **never** be pushed to GitHub.
> Store your real credentials in the [My Credentials](#my-credentials-fill-in-as-you-go) section at the bottom.

## Stack Overview

| Layer | Service | Cost |
|---|---|---|
| **Backend API** | Render Free Web Service | Free (750 hrs/month) |
| **Keep-Alive (prevent sleep)** | UptimeRobot Free | Free (5-min pings) |
| **Frontend Dashboard** | Cloudflare Pages | Free (unlimited) |
| **Database / Auth / Storage / Realtime** | Supabase Free | Free tier |
| **Extension** | Brave — Load Unpacked | Free |
| **Git Hosting** | GitHub | Free |

---

## Table of Contents

1. [Phase 1 — GitHub Setup](#phase-1--github-setup)
2. [Phase 2 — Supabase Setup](#phase-2--supabase-setup)
3. [Phase 3 — Generate Secrets](#phase-3--generate-secrets)
4. [Phase 4 — Render Backend Deployment](#phase-4--render-backend-deployment)
5. [Phase 5 — UptimeRobot Keep-Alive](#phase-5--uptimerobot-keep-alive)
6. [Phase 6 — Cloudflare Pages Frontend](#phase-6--cloudflare-pages-frontend)
7. [Phase 7 — Extension Configuration](#phase-7--extension-configuration)
8. [Phase 8 — End-to-End Verification](#phase-8--end-to-end-verification)
9. [Phase 9 — Optional Gmail API](#phase-9--optional-gmail-api)
10. [Auto-Deploy Flow](#auto-deploy-flow-once-everything-is-set-up)
11. [My Credentials](#my-credentials-fill-in-as-you-go)

---

## Phase 1 — GitHub Setup

### 1.1 Create a new GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. **Repository name**: `personal-mailtrack`
3. **Visibility**: **Private** ← important
4. Do **not** initialise with README (you already have one locally)
5. Click **Create repository**

### 1.2 Push your local repo to GitHub

```powershell
cd d:\personal-mailtrack

# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/personal-mailtrack.git
git push -u origin master
```

Verify at `https://github.com/YOUR_USERNAME/personal-mailtrack` that all files are there.

> ✅ Confirm: `DEPLOYMENT_GUIDE.md` does **not** appear on GitHub — it's gitignored.

---

## Phase 2 — Supabase Setup

### 2.1 Create a Supabase project

1. Go to [supabase.com](https://supabase.com) → **Start your project**
2. Sign up / log in with GitHub
3. Click **New project**
4. Fill in:
   - **Organization**: your personal org (auto-created)
   - **Project name**: `personal-mailtrack`
   - **Database password**: click **Generate** → copy and save it below
   - **Region**: `Southeast Asia (Singapore)` — closest to India
5. Click **Create new project**
6. Wait ~2 minutes for provisioning

### 2.2 Run the database schema

1. In your Supabase project → **SQL Editor** (left sidebar)
2. Click **New query**
3. Open `d:\personal-mailtrack\backend\supabase\schema.sql` in any text editor
4. Copy **all** the contents and paste into the SQL Editor
5. Click **Run** (▶)
6. You should see: `Success. No rows returned`

### 2.3 Create Supabase Storage buckets

Go to **Storage** (left sidebar) → create these 5 buckets, all **Private**:

| Bucket name | Public? |
|---|---|
| `documents` | ❌ Private |
| `videos` | ❌ Private |
| `avatars` | ❌ Private |
| `exports` | ❌ Private |
| `generated` | ❌ Private |

For each: **New bucket** → enter name → uncheck **Public bucket** → **Create bucket**.

### 2.4 Collect your Supabase credentials

Go to **Project Settings** → **API**:

| What | Where | Env var name |
|---|---|---|
| Project URL | Settings → API → Project URL | `SUPABASE_URL` |
| `anon` / public key | Settings → API → Project API Keys | `SUPABASE_ANON_KEY` |
| `service_role` key | Settings → API → Project API Keys | `SUPABASE_SERVICE_ROLE_KEY` |

Go to **Project Settings** → **Database** → **Connection string** → **URI** tab:

Copy the connection string and modify it:
- Replace `postgres://` at the start with `postgresql+asyncpg://`
- Replace `[YOUR-PASSWORD]` with the DB password you saved

Final result looks like:
```
postgresql+asyncpg://postgres:YOURPASSWORD@db.abcdefgh.supabase.co:5432/postgres
```

Save all four values in [My Credentials](#my-credentials-fill-in-as-you-go).

---

## Phase 3 — Generate Secrets

Run these two commands locally to generate random secret keys:

```powershell
cd d:\personal-mailtrack\backend
.\.venv\Scripts\python -c "import secrets; print('TRACKING_SIGNING_KEY=' + secrets.token_hex(32))"
.\.venv\Scripts\python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_hex(32))"
```

Copy both output values into [My Credentials](#my-credentials-fill-in-as-you-go).

> ⚠️ **Never regenerate `TRACKING_SIGNING_KEY` after going live.**
> All tracking pixels embedded in sent emails are signed with this key.
> If you must rotate it later, move the old value to `TRACKING_PREVIOUS_KEYS` first.

---

## Phase 4 — Render Backend Deployment

### 4.1 Create a Render account

1. Go to [render.com](https://render.com)
2. Sign up with **GitHub** — this allows automatic deploys on push

### 4.2 Create a new Web Service

1. Dashboard → **New** → **Web Service**
2. Select your `personal-mailtrack` GitHub repo
3. Click **Connect**

### 4.3 Configure the Web Service

| Field | Value |
|---|---|
| **Name** | `personal-mailtrack-api` |
| **Region** | `Singapore` |
| **Branch** | `master` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -e ".[dev]"` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

> Render auto-injects `$PORT` — do not hardcode `8000` in the start command.

### 4.4 Add environment variables

In the Render dashboard for your service → **Environment** tab → click **Add Environment Variable** for each row below.

Fill in the values from your Supabase credentials and generated secrets:

```
APP_ENV                     = production
API_BASE_URL                = https://personal-mailtrack-api.onrender.com
TRACKING_BASE_URL           = https://personal-mailtrack-api.onrender.com
APP_BASE_URL                = https://personal-mailtrack.pages.dev

DATABASE_URL                = postgresql+asyncpg://postgres:PASSWORD@db.YOURREF.supabase.co:5432/postgres
SUPABASE_URL                = https://YOURREF.supabase.co
SUPABASE_ANON_KEY           = eyJ...
SUPABASE_SERVICE_ROLE_KEY   = eyJ...

TRACKING_SIGNING_KEY        = (your generated hex key from Phase 3)
TRACKING_PREVIOUS_KEYS      = []
ENCRYPTION_KEY              = (your generated hex key from Phase 3)

PRIVACY_MODE                = true
EVENT_RETENTION_DAYS        = 90
TRACKING_PREPARE_TIMEOUT_MS = 2500
DEMO_MODE                   = false

FEATURE_CAMPAIGNS           = true
FEATURE_DOCUMENTS           = true
FEATURE_SIGNATURES          = true
FEATURE_POLLS               = true
FEATURE_VIDEO               = true
FEATURE_WEBHOOKS            = true
FEATURE_AI                  = false
```

> ⚠️ For `API_BASE_URL` and `TRACKING_BASE_URL`: Render assigns your URL as
> `https://YOUR-SERVICE-NAME.onrender.com`. Confirm it once the service is created,
> then come back and update these two values and **redeploy**.

### 4.5 Deploy

1. Click **Create Web Service**
2. Render pulls your repo and runs the build command (~3–5 minutes first time)
3. Watch the deploy logs — when you see `==> Your service is live 🎉` it is up

### 4.6 Confirm it is live

```
https://personal-mailtrack-api.onrender.com/health
```

Expected response:
```json
{"status": "ok", "database": "connected"}
```

Also open the interactive API docs:
```
https://personal-mailtrack-api.onrender.com/docs
```

> 💡 The Supabase schema was already applied in Phase 2 via the SQL Editor, so you do
> not need to run `initdb` in production. SQLAlchemy will connect directly to the
> existing PostgreSQL tables.

---

## Phase 5 — UptimeRobot Keep-Alive

Render free services **sleep after 15 minutes of no traffic**. Cold-start takes ~50 seconds.
During that 50 seconds, any tracking pixel request from an email will time out and the open
event will be lost. UptimeRobot pings every 5 minutes and prevents sleep entirely.

### 5.1 Create an UptimeRobot account

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up — free tier gives 50 monitors with 5-minute check intervals

### 5.2 Create a monitor

1. Dashboard → **Add New Monitor**
2. Configure:

| Field | Value |
|---|---|
| **Monitor Type** | `HTTP(s)` |
| **Friendly Name** | `Mailtrack Backend` |
| **URL** | `https://personal-mailtrack-api.onrender.com/health` |
| **Monitoring Interval** | `Every 5 minutes` |
| **Monitor Timeout** | `30 seconds` |

3. Optionally add your email under **Alert Contacts** for downtime notifications
4. Click **Create Monitor**

### 5.3 Verify

After 5 minutes, the monitor should show **Up** (green). From this point, your Render
backend will stay alive 24/7 as long as UptimeRobot is running.

> 💡 Render still restarts the container after every **new deploy** (~50 second gap).
> This is unavoidable, but happens only when you push code — not during normal use.

---

## Phase 6 — Cloudflare Pages Frontend

### 6.1 Create a Cloudflare account

1. Go to [cloudflare.com](https://cloudflare.com)
2. Sign up with your email (no credit card needed)

### 6.2 Create a Pages project

1. Dashboard → **Workers & Pages** → **Pages** (left sidebar)
2. Click **Create a project**
3. Select **Connect to Git**
4. Authorize Cloudflare to access your GitHub account
5. Select your `personal-mailtrack` repo
6. Click **Begin setup**

### 6.3 Configure the build

| Field | Value |
|---|---|
| **Project name** | `personal-mailtrack` |
| **Production branch** | `master` |
| **Framework preset** | `Vite` |
| **Build command** | `npm run build` |
| **Build output directory** | `dist` |
| **Root directory** | `dashboard` |

### 6.4 Add environment variables

Scroll to **Environment variables (advanced)** → Add:

| Variable | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://personal-mailtrack-api.onrender.com` |

### 6.5 Deploy

1. Click **Save and Deploy**
2. Cloudflare runs `npm run build` in your `dashboard/` folder (~2 minutes)
3. You get a URL like: `https://personal-mailtrack.pages.dev`

### 6.6 Update `APP_BASE_URL` on Render

Now that you have the Cloudflare Pages URL, go back to **Render → Environment** and update:

```
APP_BASE_URL = https://personal-mailtrack.pages.dev
```

Click **Manual Deploy → Deploy latest commit** to restart with the new value.

---

## Phase 7 — Extension Configuration

### 7.1 Update the extension backend URL

The extension reads `apiBaseUrl` from `chrome.storage.local`. Set it via the Options page:

1. In Brave, right-click the extension icon → **Options**
2. Set:
   - **API Base URL**: `https://personal-mailtrack-api.onrender.com`
   - **Tracking Base URL**: `https://personal-mailtrack-api.onrender.com`
3. Save

### 7.2 Rebuild the extension (if you changed source)

```powershell
cd d:\personal-mailtrack\extension
npm run build
```

Then in `brave://extensions` → click **Reload** (↺) on your extension.

### 7.3 Verify with the in-browser debugger

1. Open Gmail in Brave
2. Press **Ctrl + Shift + D**
3. The Mailtrack Debugger modal should show:
   - ✅ Brave detected
   - ✅ Backend reachable → `https://personal-mailtrack-api.onrender.com`
   - ✅ Gmail DOM selectors matched

---

## Phase 8 — End-to-End Verification

Go through this checklist after all phases are complete:

### 8.1 Backend
- [ ] `https://personal-mailtrack-api.onrender.com/health` → `{"status": "ok"}`
- [ ] `https://personal-mailtrack-api.onrender.com/docs` → Swagger UI loads
- [ ] `https://personal-mailtrack-api.onrender.com/api/v1/me` → Returns `{"user_id": ..., "mode": "personal"}`

### 8.2 Tracking pixel test

1. In the Swagger UI, call `POST /api/v1/emails` with a test payload to register a tracked email
2. Copy the returned `pixel_url`
3. Open `pixel_url` in a browser → you should see a blank page (1x1 GIF, nothing visible) with HTTP 200
4. In Supabase → **Table Editor** → `open_events` → a row should appear

### 8.3 Click redirect test

1. From the same registered email, copy one of the `tracked_links` click URLs
2. Open it in a browser → it should redirect to the original destination URL
3. In Supabase → `click_events` → a row should appear

### 8.4 Dashboard
- [ ] `https://personal-mailtrack.pages.dev` loads without errors
- [ ] Activity page shows the test open and click events
- [ ] Follow-up page loads (may be empty — that's normal)

### 8.5 Full Gmail send test
1. Open Gmail in Brave with the extension loaded
2. Compose an email to **yourself** (use a second Gmail account, Outlook, Yahoo, etc.)
3. Toggle `✓✓ Tracked` ON in the compose toolbar
4. Click **Send**
5. Open the email in the receiving inbox (Gmail or any email client)
6. Check `https://personal-mailtrack.pages.dev` → Activity page → the open should appear within seconds

### 8.6 UptimeRobot
- [ ] Monitor shows **Up** (green) on UptimeRobot dashboard
- [ ] No 50-second delays when hitting the backend API

---

## Phase 9 — Optional Gmail API

Enable this for **reply detection**, **bounce detection**, and the **Waiting on Me** queue.
Skip this if you only need open/click tracking for now.

### 9.1 Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project: `personal-mailtrack`
3. **APIs & Services** → **Library** → search `Gmail API` → **Enable**

### 9.2 Configure OAuth consent screen

1. **APIs & Services** → **OAuth consent screen**
2. User type: **External** (fine for personal use)
3. Fill in:
   - **App name**: `Personal Mailtrack`
   - **User support email**: your Gmail
4. **Scopes** → Add: `https://www.googleapis.com/auth/gmail.readonly`
5. **Test users** → Add your Gmail address(es)
6. Save

### 9.3 Create OAuth 2.0 credentials

1. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
2. Application type: **Web application**
3. Name: `Mailtrack Backend`
4. **Authorised redirect URIs** → Add:
   ```
   https://personal-mailtrack-api.onrender.com/api/v1/gmail/callback
   ```
5. Click **Create**
6. Copy `Client ID` and `Client Secret`

### 9.4 Add to Render environment variables

Go to Render → **Environment** → Add:

```
GOOGLE_CLIENT_ID      = (your Client ID)
GOOGLE_CLIENT_SECRET  = (your Client Secret)
GOOGLE_REDIRECT_URI   = https://personal-mailtrack-api.onrender.com/api/v1/gmail/callback
```

Click **Save Changes** → Render will redeploy.

### 9.5 Connect your Gmail account

1. In your browser, visit:
   ```
   https://personal-mailtrack-api.onrender.com/api/v1/gmail/auth-url
   ```
2. Copy the `url` from the JSON response
3. Open that URL in your browser → complete Google OAuth consent
4. You'll be redirected to the callback — tokens are stored in Supabase
5. Verify: `https://personal-mailtrack-api.onrender.com/api/v1/gmail/accounts` → your Gmail account appears

---

## Auto-Deploy Flow (once everything is set up)

Every time you push to GitHub, both services redeploy automatically:

```
git add -A
git commit -m "your change"
git push origin master
           ↓
       GitHub
     ↙         ↘
  Render     Cloudflare Pages
(backend)    (frontend)
~3 min       ~2 min
auto-deploys from master branch
```

During Render's redeploy, the backend restarts (~50 second gap). UptimeRobot will alert
you if the monitor detects downtime. For personal use, this brief window during deploys
is acceptable.

---

## Troubleshooting

### Render shows "Build failed"
- Check the **Logs** tab in the Render dashboard
- Most common cause: a Python dependency issue in `pyproject.toml`
- Fix locally, commit, and push — Render will auto-retry

### Cloudflare Pages shows "Build failed"
- Go to **Workers & Pages** → your project → **Deployments** → click the failed deployment → view build logs
- Most common cause: TypeScript error in the dashboard
- Fix locally (`npm run build` must succeed in `dashboard/`), commit, and push

### Extension shows "Backend unreachable" in debugger
- Confirm the backend URL in extension Options matches your Render URL exactly
- Check Render logs for any crash — the backend may be sleeping (UptimeRobot not set up yet)
- Wait 60 seconds for cold start if UptimeRobot is not running yet

### Supabase connection error in Render logs
- Double-check `DATABASE_URL` in Render environment — common mistakes:
  - `postgres://` instead of `postgresql+asyncpg://`
  - Wrong password (must be URL-encoded if it contains special chars)
  - Wrong project ref in the hostname

### Tracking pixel not recording opens
- The pixel URL must use your **production** `TRACKING_BASE_URL` (Render URL), not `localhost`
- Check that `TRACKING_SIGNING_KEY` in Render matches what was used to generate the token
- Look at Render logs when hitting the pixel URL — any `500` errors will show there

---

## Cost Summary

| Service | Free Tier Limit | Notes |
|---|---|---|
| Render | 750 hrs/month | Enough for 1 always-on service with UptimeRobot |
| Cloudflare Pages | Unlimited bandwidth, 500 builds/month | No issues for personal use |
| Supabase | 500 MB DB, 1 GB storage, 50k MAU | Plenty for personal use |
| UptimeRobot | 50 monitors, 5-min interval | Free forever |
| GitHub | Unlimited private repos | Free |

**Total monthly cost: $0**

---

## My Credentials (fill in as you go)

> 🔒 This section is in a gitignored file — safe to fill in here.
> Never put these values in any committed file.

```
=== GITHUB ===
Username          :
Repo URL          : https://github.com/YOUR_USERNAME/personal-mailtrack

=== SUPABASE ===
Project Name      : personal-mailtrack
Project Ref       :
DB Password       :
Project URL       : https://__________.supabase.co
Anon Key          : eyJ...
Service Role Key  : eyJ...
DATABASE_URL      : postgresql+asyncpg://postgres:PASSWORD@db.REF.supabase.co:5432/postgres

=== GENERATED SECRETS ===
TRACKING_SIGNING_KEY :
ENCRYPTION_KEY       :

=== RENDER ===
Service Name      : personal-mailtrack-api
Service URL       : https://personal-mailtrack-api.onrender.com
Dashboard URL     : https://dashboard.render.com

=== CLOUDFLARE PAGES ===
Project Name      : personal-mailtrack
Pages URL         : https://personal-mailtrack.pages.dev
Custom Domain     : (leave blank until you own a domain)

=== UPTIMEROBOT ===
Monitor Name      : Mailtrack Backend
Monitor URL       : https://personal-mailtrack-api.onrender.com/health
Dashboard         : https://uptimerobot.com/dashboard

=== GOOGLE OAUTH (Optional — Phase 9) ===
Cloud Project ID  : personal-mailtrack
Client ID         :
Client Secret     :
Redirect URI      : https://personal-mailtrack-api.onrender.com/api/v1/gmail/callback
```
