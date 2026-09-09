# MASTER BUILD PROMPT

# Personal Mailtrack / Mailsuite-Style Email Productivity Suite

## Python + FastAPI + Supabase + Brave + Gmail

## Free-Tier-First, Single-User Personal Project

---

# 0. YOUR ROLE

You are a senior Python backend engineer, browser-extension engineer, security engineer, database architect, and product engineer.

Your task is to design and implement a **personal-use Gmail email-tracking and productivity system inspired by the feature set of Mailtrack/Mailsuite**, but implemented as an original clean-room project.

Do NOT copy proprietary source code, private APIs, branding, UI assets, or implementation details from Mailtrack/Mailsuite.

Build equivalent functionality using:

* Python
* FastAPI
* Supabase
* PostgreSQL
* Supabase Auth
* Supabase Storage
* Supabase Realtime
* Chrome/Chromium Manifest V3
* Brave browser
* Gmail Web
* Gmail API
* React + TypeScript for the dashboard where useful

The project is for **one person using their own Gmail accounts**.

It is NOT a SaaS product.

Do not build unnecessary:

* billing
* subscriptions
* enterprise SSO
* organization administration
* multi-tenant SaaS infrastructure
* team dashboards
* usage-based billing
* enterprise admin panels

However, keep the database logically extensible by retaining ownership identifiers such as `user_id`.

---

# 1. PRIMARY OBJECTIVE

Build a personal email productivity platform that provides the most useful capabilities of a premium Mailtrack/Mailsuite-style product, directly integrated into Gmail.

The end result should allow the user to:

* know when sent emails are opened;
* know when links are clicked;
* see exactly which recipient engaged where technically possible;
* see engagement history;
* receive real-time notifications;
* detect hot conversations;
* detect revived/old conversations;
* receive no-reply reminders;
* detect replies;
* detect bounces;
* schedule tracked messages;
* run personalized mail-merge campaigns;
* track PDFs;
* see page-by-page document analytics;
* securely share documents;
* request signatures;
* manage contacts;
* manage templates;
* run polls;
* send tracked video links;
* export analytics;
* create webhook automations;
* view productivity reports;
* eventually support AI-powered productivity features.

The system should feel like a natural extension of Gmail rather than a separate application.

---

# 2. USER AND ENVIRONMENT ASSUMPTIONS

The primary user:

* uses **Brave browser**;
* uses **Gmail Web**;
* may own multiple Gmail accounts;
* wants the system for personal use;
* does not currently own a custom domain;
* wants to stay on free tiers wherever possible;
* does not want to maintain complex server infrastructure;
* is comfortable running Python and Docker locally;
* eventually may deploy the backend publicly.

Primary browser:

> Brave Desktop

Because Brave is Chromium-based, develop the extension as a standard Chromium Manifest V3 extension.

Primary email provider:

> Gmail / Google Workspace through the Gmail API and Gmail Web.

Initial deployment must work **without owning a custom domain**.

Design the tracking URLs so they can later migrate from a temporary hosting URL to:

```text
api.example.com
track.example.com
app.example.com
```

without redesigning the application.

---

# 3. CORE TECHNOLOGY STACK

Use:

## Backend

```text
Python 3.12+
FastAPI
Pydantic v2
Uvicorn
SQLAlchemy 2.x
```

## Database / platform

```text
Supabase PostgreSQL
Supabase Auth
Supabase Storage
Supabase Realtime
```

## Gmail

```text
Gmail API
Google OAuth 2.0
Google Pub/Sub only if truly useful and available
```

Do not unnecessarily build a custom SMTP server.

## Frontend

```text
React
TypeScript
Vite
```

## Extension

```text
Manifest V3
TypeScript/JavaScript
Chrome/Chromium extension APIs
```

## Background work

Prefer the simplest free-tier-friendly architecture.

Do NOT introduce Redis + Celery by default.

First implement:

```text
FastAPI BackgroundTasks
```

and lightweight scheduled mechanisms.

Only introduce a queue system where the feature genuinely requires durable asynchronous execution.

The architecture must make it easy to add Celery/Redis later without rewriting domain logic.

---

# 4. FREE-TIER-FIRST PRINCIPLE

Every architectural choice must answer:

> Can this be accomplished with fewer services?

Prefer:

```text
Supabase
+
FastAPI
+
Gmail API
+
Brave extension
```

over a large collection of infrastructure services.

Do not introduce infrastructure merely because it is "industry standard."

Avoid initially requiring:

* Redis
* Celery
* RabbitMQ
* Kafka
* MinIO
* Kubernetes
* Pusher
* Reverb
* Elasticsearch
* dedicated PostgreSQL
* dedicated object storage
* dedicated authentication server

Use Supabase's managed functionality wherever appropriate.

---

# 5. ARCHITECTURAL PRINCIPLE

Use this separation:

```text
Brave Extension
        |
        v
     FastAPI
        |
   ┌────┼───────────────┐
   |    |               |
   v    v               v
Gmail  Business       Tracking
API    Logic          Engine
   |        |             |
   └────────┼─────────────┘
            |
            v
        Supabase
     ┌────┬────┬────┬────┐
     |    |    |    |
  DB/Auth Storage Realtime
```

FastAPI is the application brain.

Supabase is the managed infrastructure/data platform.

---

# 6. EVENT-FIRST ARCHITECTURE

The most important architectural decision:

> Events are the canonical representation of activity.

Do not implement each feature as an isolated tracking mechanism.

Create a unified event model.

Examples:

```text
email.sent
email.delivered
email.opened
email.clicked
email.replied
email.bounced
email.unsubscribed

document.opened
document.page_viewed
document.downloaded
document.signed

campaign.created
campaign.scheduled
campaign.started
campaign.message_sent
campaign.completed
campaign.paused
campaign.cancelled

contact.created
contact.updated
contact.engaged

followup.created
followup.due
followup.triggered
followup.dismissed

video.opened
video.played
video.progress

poll.viewed
poll.responded

signature.requested
signature.viewed
signature.completed
```

Every downstream system should consume these events.

For example:

```text
email.opened
     |
     +----> analytics
     |
     +----> notification engine
     |
     +----> CRM timeline
     |
     +----> engagement score
     |
     +----> automation engine
     |
     +----> webhook
```

This allows future functionality to be added without modifying the underlying tracking engine.

---

# 7. DATABASE MODEL

Use Supabase PostgreSQL.

Use UUIDs for public identifiers.

Use database-generated numeric IDs only where useful internally.

All timestamps:

```text
TIMESTAMPTZ
UTC
```

Required tables:

```text
profiles
gmail_accounts
oauth_credentials

tracked_emails
email_recipients
tracked_links

open_events
click_events
reply_events
bounce_events
delivery_events

contacts
contact_lists
contact_list_members
contact_notes

campaigns
campaign_recipients
campaign_events

email_templates

scheduled_emails

notification_rules
notification_events

automation_rules
automation_runs

documents
document_shares
document_events

signature_requests
signature_fields
signature_events

polls
poll_options
poll_responses

videos
video_events

webhook_endpoints
webhook_deliveries

activity_events

user_settings
```

---

# 8. DATA MODEL DETAILS

## profiles

```text
id UUID PK
email
display_name
timezone
created_at
updated_at
```

Use Supabase Auth user ID as the ownership identity.

Do not build custom password storage.

---

## gmail_accounts

Support multiple personally owned Gmail accounts.

Fields:

```text
id UUID
user_id UUID
google_account_id TEXT
email CITEXT
display_name TEXT
picture_url TEXT NULL
is_default BOOLEAN
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

---

## oauth_credentials

Store encrypted OAuth refresh/access credentials.

Never expose refresh tokens to the browser.

Prefer server-side encrypted storage.

Fields:

```text
id
gmail_account_id
access_token_encrypted
refresh_token_encrypted
expires_at
scopes
created_at
updated_at
```

---

# 9. EMAIL DATA MODEL

Do NOT use one table containing:

```text
email -> recipient
```

as the complete abstraction.

Use:

```text
tracked_emails
       |
       +---- email_recipients
       |
       +---- tracked_links
```

This is necessary for individual recipient tracking and campaigns.

---

## tracked_emails

```text
id UUID
user_id UUID
gmail_account_id UUID
public_id UUID
gmail_message_id TEXT NULL
gmail_thread_id TEXT NULL
rfc_message_id TEXT NULL
subject TEXT NULL
snippet TEXT NULL
campaign_id UUID NULL
sent_at TIMESTAMPTZ
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

---

## email_recipients

```text
id UUID
tracked_email_id UUID
contact_id UUID NULL
email CITEXT
name TEXT NULL
recipient_type TEXT
tracking_token_id UUID
first_open_at TIMESTAMPTZ NULL
last_open_at TIMESTAMPTZ NULL
first_click_at TIMESTAMPTZ NULL
last_click_at TIMESTAMPTZ NULL
human_open_count INTEGER DEFAULT 0
human_click_count INTEGER DEFAULT 0
reply_received_at TIMESTAMPTZ NULL
bounced_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
```

---

# 10. GROUP EMAIL TRACKING

Understand this constraint:

A single identical MIME message sent to multiple recipients cannot intrinsically identify which recipient loaded the same shared pixel.

Therefore:

## Normal Gmail send

Support:

```text
one sender
one or multiple recipients
```

but label recipient-level attribution according to what is technically observable.

## Campaign / mail merge

For exact recipient-level attribution:

```text
one individualized outgoing message
per recipient
```

Each gets:

```text
recipient-specific pixel
recipient-specific tracking links
recipient-specific event identity
```

Do not pretend shared pixels provide recipient identity.

---

# 11. TRACKING TOKEN SYSTEM

Use HMAC-signed opaque tokens.

Use:

```text
TRACKING_SIGNING_KEY
```

from environment/secret storage.

Never expose:

* sequential DB IDs;
* raw internal UUIDs where avoidable;
* secrets.

Implement:

```python
generate_open_token(...)
verify_open_token(...)

generate_click_token(...)
verify_click_token(...)
```

Use:

```python
hmac.compare_digest(...)
```

for verification.

Support future key rotation:

```text
key_id
active_key
previous_keys
```

---

# 12. OPEN TRACKING

Endpoint:

```text
GET /t/o/{token}
```

Requirements:

1. validate token syntax;
2. verify HMAC without querying DB where possible;
3. decode recipient tracking identity;
4. record event;
5. publish activity;
6. return immediately.

Do not:

* call external geo-IP APIs synchronously;
* perform analytics;
* run expensive bot detection synchronously;
* call Gmail;
* perform slow document operations.

Return a 1x1 transparent GIF.

Headers:

```text
Content-Type: image/gif
Cache-Control: no-store, no-cache, must-revalidate, max-age=0
Pragma: no-cache
Expires: 0
X-Content-Type-Options: nosniff
```

Invalid tracking token:

* same generic pixel;
* HTTP 200;
* no event insertion;
* no detailed error.

---

# 13. CLICK TRACKING

Endpoint:

```text
GET /t/c/{token}?u=<encoded-url>
```

The token must cryptographically bind:

```text
recipient_tracking_id
+
exact destination URL
```

Validation requirements:

* scheme must be http or https;
* hostname required;
* reject javascript;
* reject data;
* reject vbscript;
* reject file;
* reject protocol-relative URLs;
* reject malformed URLs;
* reject userinfo unless explicitly supported;
* maximum URL length;
* reject localhost;
* reject loopback addresses;
* reject private IP ranges;
* reject link-local;
* reject multicast;
* reject unspecified/reserved destinations.

Never redirect an unverified URL.

Success:

```text
insert click event
publish click event
302 redirect
```

---

# 14. TRACKED LINKS

For each eligible link:

```text
tracked_links
```

store:

```text
id
tracked_email_id
original_url
normalized_url
link_text
position
```

Link analytics should support:

```text
total clicks
unique clicks
first click
last click
clicks by recipient
clicks by link
click timestamp
```

---

# 15. GMAIL EXTENSION

Target:

```text
Brave Desktop
+
Gmail Web
```

Use Manifest V3.

Keep all Gmail DOM selectors centralized.

Create:

```text
extension/
  background/
  content/
  popup/
  options/
  shared/
```

Core modules:

```text
gmail-compose.ts
gmail-sent.ts
gmail-inbox.ts
gmail-thread.ts
gmail-sidebar.ts
tracking-injector.ts
link-rewriter.ts
notifications.ts
api-client.ts
auth.ts
settings.ts
```

---

# 16. GMAIL COMPOSE FEATURES

The compose integration should support:

```text
Tracking ON/OFF
Link tracking ON/OFF
PDF tracking
Schedule
Campaign
Template
Poll
Video
Signature request
```

The UI must feel native.

Do not build one giant extension file.

---

# 17. SEND INTERCEPTION

When the user presses Send:

1. detect compose;
2. capture send action;
3. determine whether tracking is enabled;
4. read:

   * sender;
   * recipients;
   * subject;
   * body;
   * links;
   * attachments where relevant;
5. register tracking with FastAPI;
6. inject pixel;
7. rewrite eligible links;
8. optionally convert document attachments to tracked links;
9. trigger original Gmail Send.

Critical:

> Tracking setup must fail open.

If backend/API is unavailable:

```text
send the email normally
```

Never leave the user unable to send because your tracker is down.

Timeout tracking preparation quickly.

---

# 18. DOUBLE-SEND PREVENTION

Use an explicit internal flag/state.

Example:

```text
trackingSendInProgress
```

Never allow your extension's re-triggered send to be intercepted a second time.

Add tests for:

* mouse Send;
* keyboard Send;
* retry;
* slow API;
* API failure;
* Gmail UI change;
* extension reload.

---

# 19. GMAIL SENT UI

Add indicators similar to Mailtrack-style checkmarks:

```text
✓   sent/tracked
✓✓  opened
↗   clicked
↩   replied
⚠   bounced
🔥   hot
```

Do not make the exact visual symbols a proprietary clone.

Use original visual treatment.

Hover/click should show:

```text
First opened:
Last opened:
Open count:
Last click:
Click count:
Reply:
```

---

# 20. REAL-TIME ACTIVITY

Use Supabase Realtime where practical.

Do not subscribe the browser to every raw database mutation.

Prefer a controlled activity/broadcast model.

For example:

```text
event occurs
   ↓
activity_events
   ↓
Supabase Realtime
   ↓
dashboard/extension
```

Events:

```text
email.opened
email.clicked
email.replied
email.bounced
document.opened
document.page_viewed
signature.completed
```

The extension may not maintain a permanent connection because Manifest V3 service workers are ephemeral.

Therefore:

* realtime while popup/dashboard is active;
* periodic reconciliation;
* optional browser notifications;
* authoritative state always comes from API/database.

---

# 21. ACTIVITY TIMELINE

Create a unified activity timeline.

Example:

```text
09:41  Sent "Project Proposal"
09:44  Opened
09:45  Clicked pricing link
09:47  Proposal PDF opened
09:48  Page 4 viewed
09:56  Reopened email
10:22  Reply received
```

This should be the central UX of the product.

---

# 22. OPEN ANALYTICS

Track:

```text
first open
last open
total raw opens
human-likely opens
bot/proxy opens
open timestamps
client
OS
device
coarse location where permitted
```

Distinguish:

```text
raw event
```

from:

```text
interpreted human-likely event
```

Never delete raw events solely because they are suspected bots.

---

# 23. BOT/PREFETCH CLASSIFICATION

Create:

```text
EventClassifier
```

It should evaluate:

* timing after send;
* user agent;
* known image proxies;
* security scanner behavior;
* request patterns;
* IP/ASN characteristics where practical.

Classifications:

```text
human_likely
proxy_likely
security_scanner_likely
automation_likely
unknown
```

Store:

```text
classification
confidence
reason
```

The dashboard should clearly distinguish:

```text
Raw activity
```

from:

```text
Likely human engagement
```

Do not claim perfect open detection.

---

# 24. GEOLOCATION

This is optional.

For personal use, prefer a free/local GeoIP database if possible.

Do not make a paid API mandatory.

Possible data:

```text
country
region
city
```

Privacy mode should allow disabling location entirely.

Avoid storing precise location unless necessary.

---

# 25. EMAIL NOTIFICATION ENGINE

Implement configurable rules.

Notification types:

```text
first open
every open
first click
every click
PDF viewed
follow-up due
no reply
hot conversation
revival
reply
bounce
campaign complete
document signed
```

Channels:

```text
Chrome desktop
dashboard
email
webhook
```

Notifications need:

```text
cooldown
deduplication
enabled/disabled
conditions
```

Prevent notification spam.

---

# 26. HOT CONVERSATION

Default rule:

```text
same recipient
+
multiple opens
+
short time window
```

Example:

```text
3+ likely-human opens
within 30 minutes
```

Allow configurable thresholds.

---

# 27. REVIVAL ALERT

Detect:

```text
old email
+
new likely-human engagement
```

Example default:

```text
no open for 7+ days
then new open
```

Notify:

```text
"Your old email was reopened"
```

---

# 28. FOLLOW-UP / NO-REPLY

Support:

```text
24 hours
48 hours
72 hours
custom duration
```

Track:

```text
sent
no reply
reply received
reminder triggered
reminder dismissed
```

Once reply is detected:

```text
cancel outstanding no-reply reminder
```

---

# 29. REPLY DETECTION

Use Gmail API.

Correlate using:

```text
gmail thread ID
gmail message ID
RFC Message-ID
In-Reply-To
References
```

Never rely only on subject matching.

When a reply arrives:

```text
reply_event
contact timeline update
email status update
notification
automation trigger
```

---

# 30. EMAIL PRODUCTIVITY ANALYTICS

Dashboard should show:

```text
emails sent
emails replied to
average response time
average reply time
tracked opens
tracked clicks
PDF views
follow-ups
no-reply rate
reply rate
```

Do not present fabricated statistics.

Clearly define formulas.

---

# 31. CAMPAIGNS

Build a campaign engine.

Campaign structure:

```text
campaign
 ├── recipients
 ├── content
 ├── personalization
 ├── schedule
 ├── tracking
 ├── bounce state
 ├── unsubscribe state
 ├── reply state
 └── analytics
```

Support:

```text
CSV import
Google Sheets import later
contact lists
manual recipient entry
template selection
personalized variables
preview
schedule
pause
cancel
send batches
```

---

# 32. MAIL MERGE

Variables:

```text
{{first_name}}
{{last_name}}
{{email}}
{{company}}
{{phone}}
{{custom_field}}
```

Use a safe rendering engine.

Never execute arbitrary code from templates.

Preview each recipient.

Support fallback:

```text
{{first_name | fallback: "there"}}
```

or an equivalent safe syntax.

---

# 33. CAMPAIGN TRACKING

Each campaign recipient gets a unique:

```text
email recipient
tracking identity
```

Track:

```text
sent
opened
opened count
clicked
clicked count
PDF viewed
replied
bounced
unsubscribed
```

Campaign dashboard:

```text
recipients
sent
delivered
open rate
click rate
reply rate
bounce rate
unsubscribe rate
PDF engagement
```

---

# 34. CAMPAIGN SEND SAFETY

Because Gmail is being used personally:

Implement configurable:

```text
daily send limit
hourly send limit
batch size
delay between batches
```

Do not try to bypass Google's anti-abuse controls.

Do not build spam-evasion mechanisms.

Provide:

```text
pause campaign
cancel campaign
```

at all times.

---

# 35. SCHEDULING

Support:

```text
send later
schedule campaign
timezone-aware scheduling
cancel
reschedule
```

For a personal free-tier architecture:

Prefer simple persistent scheduled records plus periodic execution.

Make sending idempotent.

A scheduled message must never send twice because a worker restarted.

---

# 36. CONTACT CRM

Contact fields:

```text
name
email
company
phone
tags
notes
last contacted
last opened
last clicked
last replied
engagement score
```

Views:

```text
recently engaged
hot
never opened
no reply
replied
bounced
unsubscribed
```

---

# 37. CONTACT TIMELINE

Every important interaction should appear chronologically.

Example:

```text
Email sent
Email opened
Pricing clicked
Proposal viewed
Reply received
Follow-up scheduled
```

This is more important than having dozens of separate analytics screens.

---

# 38. EMAIL TEMPLATES

Support:

```text
subject
HTML body
plain text body
variables
category
favorite
```

Actions:

```text
create
edit
duplicate
delete
insert into Gmail
```

Template insertion must preserve Gmail signatures where possible.

---

# 39. TRACKED BUTTONS

Allow the user to insert an attractive CTA:

```text
View Proposal
Book Meeting
See Pricing
Download
```

The underlying destination should still use signed click tracking.

---

# 40. POLLS / SURVEYS

Support simple tracked choices:

```text
Are you interested?

[Yes]
[No]
```

Each option gets a signed tracking URL.

Record:

```text
poll_id
recipient
option
timestamp
```

Dashboard:

```text
responses
response rate
option distribution
```

---

# 41. VIDEO MESSAGES

Do not directly embed large video files into Gmail.

Instead:

```text
upload video
    ↓
secure hosted page
    ↓
tracked link
```

Record:

```text
page opened
video started
video progress
video completed
CTA clicked
```

Use Supabase Storage for files.

---

# 42. PDF / DOCUMENT TRACKING

This should be a major feature.

For tracked PDFs:

```text
upload PDF
    ↓
store securely
    ↓
generate document
    ↓
create share
    ↓
email contains tracked document link
    ↓
recipient sees secure viewer
```

Do not pretend an ordinary Gmail PDF attachment can provide page-by-page analytics.

Use a hosted document viewer.

---

# 43. DOCUMENT VIEWER

Use:

```text
PDF.js
```

where appropriate.

Track:

```text
document opened
page viewed
page duration
percentage viewed
downloaded
```

Example:

```text
Page 1: 4 sec
Page 2: 12 sec
Page 3: 41 sec
Page 4: 2 sec
```

Aggregate:

```text
total time
percentage viewed
most viewed pages
```

---

# 44. DOCUMENT SHARING

Support:

```text
secure URL
expiration
download allowed/disabled
password
recipient email verification
```

Use private Supabase Storage.

Generate signed URLs/tokens.

Do not make sensitive documents public.

---

# 45. CONFIDENTIAL WATERMARKS

Allow watermarking of generated/derived document copies.

Example:

```text
CONFIDENTIAL
recipient@example.com
2026-09-09
```

Do not overwrite the original source file.

Store:

```text
original
watermarked derivative
```

separately.

---

# 46. DOCUMENT NOTIFICATIONS

Support:

```text
document opened
first page viewed
document downloaded
document completed
```

Users can disable each.

---

# 47. E-SIGNATURE

Implement as a separate module.

Features:

```text
upload PDF
select signer
place fields
text field
date field
signature field
send request
signer view
signature completion
audit trail
signed PDF
```

Audit trail:

```text
request created
document viewed
signature started
signature completed
timestamp
signer identity
document hash
```

Do not claim legal equivalence to regulated qualified digital signatures.

---

# 48. CERTIFIED EMAIL / DELIVERY CERTIFICATE

Generate an evidence report containing:

```text
sender
recipient
subject
message identifiers
sent time
delivery/bounce events
tracking events
reply events
event hashes
```

Export as PDF/JSON.

Make clear:

> Tracking evidence does not automatically prove that a human read or understood the message.

---

# 49. CUSTOM UNSUBSCRIBE

For campaigns, implement:

```text
GET /u/{token}
```

Features:

```text
unsubscribe
global suppression
campaign/list suppression
resubscribe
```

Campaign sending must check suppression before every send.

Never send to an unsubscribed contact.

---

# 50. BOUNCE DETECTION

Depending on Gmail capabilities and sending method:

Support:

```text
hard bounce
soft bounce
complaint where available
unknown
```

Store:

```text
smtp/provider code
diagnostic
timestamp
```

Hard bounced contacts should be automatically suppressed from campaigns.

---

# 51. WEBHOOKS

Allow the user to register:

```text
POST endpoint
secret
events
enabled
```

Events:

```text
email.opened
email.clicked
email.replied
email.bounced

document.opened
document.downloaded
document.signed

campaign.completed
```

Sign payloads.

Example:

```text
X-Webhook-Signature
```

Use retry/backoff.

Deduplicate deliveries.

---

# 52. GENERIC AUTOMATION ENGINE

Create:

```text
automation_rules
automation_runs
```

Rule structure:

```text
WHEN
  event

IF
  conditions

THEN
  actions
```

Example:

```text
WHEN email.opened

IF
  open_count >= 3

THEN
  desktop notification
  webhook
```

Another:

```text
WHEN document.opened

IF
  recipient is tagged "client"

THEN
  update contact score
```

Another:

```text
WHEN no_reply_due

THEN
  notify user
```

This should eventually make the product extensible beyond fixed notification types.

---

# 53. ENGAGEMENT SCORE

Implement an optional heuristic score.

Example:

```text
open              +1
reopen            +2
link click        +5
important CTA     +10
PDF open          +5
PDF page reading  +8
reply             +20
bounce            -50
unsubscribe       -100
```

Make weights configurable.

Do not claim this is scientific.

Display:

```text
Hot
Warm
Cold
```

or a score such as:

```text
73 / 100
```

---

# 54. DASHBOARD

Pages:

```text
/login

/activity

/emails
/emails/:id

/contacts
/contacts/:id

/campaigns
/campaigns/new
/campaigns/:id

/templates

/documents
/documents/:id

/reports

/settings
/settings/gmail
/settings/tracking
/settings/notifications
/settings/privacy
/settings/integrations
```

---

# 55. ACTIVITY DASHBOARD

The main dashboard should prioritize:

```text
Recent activity
Unread/opened state
Hot conversations
Follow-ups due
No replies
Recent clicks
Recent PDF activity
Replies
Bounces
```

It should answer:

> "What happened with my emails recently?"

within seconds.

---

# 56. REPORTING

Daily report:

```text
emails sent
opens
clicks
replies
PDF views
bounces
follow-ups
```

Weekly/monthly report:

```text
sent
opened
clicked
replied
top contacts
top links
best-performing campaigns
PDF engagement
average response time
```

Allow CSV export.

Optional PDF report generation.

---

# 57. EMAIL SEARCH / FILTER

Search by:

```text
subject
recipient
contact
campaign
date
status
```

Filters:

```text
opened
unopened
clicked
replied
bounced
hot
revived
PDF viewed
```

---

# 58. PRIVACY SETTINGS

Provide:

```text
privacy mode
store IP yes/no
store precise location yes/no
store raw user agent yes/no
retention period
automatic deletion
```

Default to privacy-conscious storage.

Support recipient data deletion.

---

# 59. DATA RETENTION

Make configurable:

```text
EVENT_RETENTION_DAYS=90
```

Allow:

```text
30
90
180
365
forever
```

depending on personal preference.

Implement cleanup safely.

---

# 60. SUPABASE AUTH

Do not build custom auth.

Use:

```text
Supabase Auth
```

Support initially:

```text
email/password
magic link
```

Optional later:

```text
Google OAuth
```

The dashboard should authenticate with Supabase.

FastAPI should validate authenticated requests.

---

# 61. AUTH FLOW

Recommended:

```text
Brave
   ↓
Dashboard
   ↓
Supabase Auth
   ↓
session/JWT
   ↓
FastAPI
   ↓
database
```

Extension should not store the dashboard session cookie.

Use a secure extension-specific authentication flow.

---

# 62. EXTENSION AUTH

Implement:

```text
user logs into extension
       ↓
extension gets short/long-lived credential
       ↓
secure chrome.storage.local
```

Never:

* put secrets in page DOM;
* use localStorage;
* inject secrets into Gmail content.

Provide:

```text
logout
revoke extension
```

---

# 63. GMAIL OAUTH

Support connecting multiple personally owned Gmail accounts.

Required capabilities should be minimized.

Store:

```text
account identity
scopes
encrypted refresh token
```

Do not request broad Gmail scopes unless required.

---

# 64. GMAIL API USAGE

Use Gmail API for:

```text
message metadata
thread metadata
sent correlation
reply detection
optional scheduled/campaign support
```

Do not continuously download entire mailbox contents.

Use incremental synchronization wherever possible.

---

# 65. OPTIONAL GMAIL PUSH

If practical within free-tier/project constraints, support Gmail watch/push for reply detection.

Otherwise implement lightweight periodic synchronization.

Do not make Google Pub/Sub mandatory for first MVP if it materially complicates deployment.

---

# 66. MOBILE

Do NOT initially build:

```text
Android app
iOS app
Gmail mobile add-on
```

Architect the backend so a mobile client could be added later.

The first target is:

> Brave + Gmail Web.

---

# 67. CUSTOM DOMAIN

User currently does not own a domain.

Therefore custom domains are NOT an MVP prerequisite.

Use:

```text
temporary deployed HTTPS hostname
```

for tracking.

Architect configuration:

```text
TRACKING_BASE_URL
API_BASE_URL
APP_BASE_URL
```

so a future domain change requires configuration changes rather than a code rewrite.

Later support:

```text
track.example.com
api.example.com
app.example.com
```

---

# 68. STORAGE

Use Supabase Storage.

Private buckets:

```text
documents
videos
avatars
exports
generated
```

Never make private documents public by default.

Use signed URLs or application-authorized access.

---

# 69. FILE SECURITY

For uploaded files:

* validate MIME type;
* validate extension;
* enforce size limits;
* compute SHA-256;
* assign generated storage key;
* never trust user filename for storage path;
* scan/sanitize where practical;
* never directly execute uploaded content.

---

# 70. SECURITY

Implement:

```text
strict CORS
CSRF protection where cookie auth is used
secure cookies
rate limits
input validation
ownership checks
Supabase RLS
signed tracking tokens
signed click destinations
SSRF-safe URL validation
safe HTML sanitization
secret management
audit logging
```

---

# 71. SUPABASE RLS

Every user-owned table must have RLS.

Typical principle:

```text
auth.uid() = user_id
```

For derived ownership:

```text
tracked_email.user_id = auth.uid()
```

through relational ownership.

Do not assume frontend filtering is security.

The database must enforce access.

---

# 72. SERVICE ROLE KEY

The Supabase service-role key must NEVER be sent to:

* browser;
* extension;
* public JavaScript;
* client-side React.

It can exist only server-side.

---

# 73. API DESIGN

Use:

```text
/api/v1/
```

Version the API from the beginning.

Suggested endpoints:

```text
GET    /me

GET    /gmail/accounts
POST   /gmail/accounts
DELETE /gmail/accounts/{id}

POST   /emails
GET    /emails
GET    /emails/{id}
GET    /emails/{id}/timeline

GET    /contacts
POST   /contacts
PATCH  /contacts/{id}
DELETE /contacts/{id}

GET    /campaigns
POST   /campaigns
GET    /campaigns/{id}
PATCH  /campaigns/{id}
POST   /campaigns/{id}/preview
POST   /campaigns/{id}/schedule
POST   /campaigns/{id}/send
POST   /campaigns/{id}/pause
POST   /campaigns/{id}/cancel

GET    /templates
POST   /templates
PATCH  /templates/{id}
DELETE /templates/{id}

POST   /documents
GET    /documents
POST   /documents/{id}/shares
GET    /documents/{id}/analytics

GET    /analytics/summary
GET    /analytics/activity
GET    /analytics/campaigns
GET    /analytics/contacts
GET    /analytics/export

GET    /notifications
GET    /notification-rules
POST   /notification-rules
PATCH  /notification-rules/{id}

GET    /automations
POST   /automations
PATCH  /automations/{id}

GET    /webhooks
POST   /webhooks
PATCH  /webhooks/{id}
DELETE /webhooks/{id}
```

Public endpoints:

```text
GET /t/o/{token}
GET /t/c/{token}
GET /d/{share_token}
POST /d/{share_token}/event
GET /u/{token}
```

---

# 74. PYTHON PROJECT STRUCTURE

Use a modular architecture:

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── jwt.py
│   │   └── oauth.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── gmail.py
│   │   ├── emails.py
│   │   ├── tracking.py
│   │   ├── contacts.py
│   │   ├── campaigns.py
│   │   ├── templates.py
│   │   ├── documents.py
│   │   ├── analytics.py
│   │   ├── notifications.py
│   │   ├── automation.py
│   │   └── webhooks.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   │   ├── tracking/
│   │   ├── gmail/
│   │   ├── campaigns/
│   │   ├── analytics/
│   │   ├── documents/
│   │   ├── notifications/
│   │   ├── automation/
│   │   └── contacts/
│   │
│   ├── jobs/
│   ├── security/
│   │   ├── tracking_tokens.py
│   │   ├── url_safety.py
│   │   └── encryption.py
│   │
│   └── utils/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── pyproject.toml
├── .env.example
└── Dockerfile
```

---

# 75. EXTENSION STRUCTURE

```text
extension/
├── manifest.json
├── background/
│   ├── service-worker.ts
│   ├── api-client.ts
│   ├── auth.ts
│   ├── sync.ts
│   └── notifications.ts
│
├── content/
│   ├── selectors.ts
│   ├── compose.ts
│   ├── sent.ts
│   ├── inbox.ts
│   ├── thread.ts
│   ├── injector.ts
│   └── sidebar.ts
│
├── popup/
│   ├── popup.html
│   ├── popup.ts
│   └── popup.css
│
├── options/
│   ├── options.html
│   └── options.ts
│
├── shared/
│   ├── types.ts
│   ├── constants.ts
│   └── storage.ts
│
└── icons/
```

---

# 76. DASHBOARD STRUCTURE

```text
dashboard/
├── src/
│   ├── pages/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── stores/
│   ├── types/
│   └── utils/
├── package.json
└── Dockerfile
```

Use a simple, information-dense design.

Do not overdesign.

---

# 77. TESTING REQUIREMENTS

Implement tests before calling a major milestone complete.

## Tracking token tests

Test:

```text
valid token
tampered token
truncated token
malformed token
wrong key
wrong recipient
```

## Click security

Reject:

```text
javascript:
data:
file:
localhost
127.0.0.1
10.x.x.x
172.16.x.x
192.168.x.x
::1
private IPv6
```

## Extension

Test:

```text
normal send
keyboard send
tracking disabled
backend unavailable
slow backend
double-send prevention
multiple links
no links
attachment
signature
campaign
```

## Campaign

Test:

```text
personalization
duplicate recipient
unsubscribed recipient
bounce
pause
resume
cancel
retry
idempotency
```

## Analytics

Hand-check all formulas.

## Security

Attempt:

```text
cross-user access
forged token
unsafe redirect
RLS bypass from client
service-role exposure
```

---

# 78. END-TO-END TEST

A mandatory happy-path test:

```text
1. User opens Gmail in Brave.
2. User composes email.
3. Tracking is ON.
4. User sends email.
5. Email arrives in controlled second inbox.
6. Pixel request reaches backend.
7. Event appears in Supabase.
8. Dashboard shows "opened."
9. Recipient clicks tracked link.
10. Click event appears.
11. Dashboard updates in realtime.
12. Recipient replies.
13. Reply appears in timeline.
14. No-reply reminder is cancelled.
```

---

# 79. SECOND END-TO-END TEST

Campaign:

```text
1. Import 5 contacts.
2. Create campaign.
3. Add personalization.
4. Preview.
5. Schedule.
6. Send.
7. Each recipient gets individualized tracking.
8. Open some messages.
9. Click different links.
10. Reply to one.
11. Bounce one.
12. Unsubscribe one.
13. Dashboard computes analytics correctly.
```

---

# 80. THIRD END-TO-END TEST

PDF:

```text
1. Upload PDF.
2. Create secure share.
3. Insert tracked document into Gmail.
4. Send.
5. Open document.
6. View pages 1–4.
7. Spend different times on pages.
8. Download.
9. Dashboard shows page-level analytics.
10. Expiration blocks access afterward.
```

---

# 81. OBSERVABILITY

Keep logging simple.

Structured logs:

```text
request_id
user_id
event_id
route
duration_ms
error
```

Never log:

```text
passwords
API tokens
OAuth refresh tokens
tracking signing key
service role key
full sensitive payloads
```

Add `/health`.

---

# 82. CONFIGURATION

Use `.env`.

Example:

```dotenv
APP_ENV=development

API_BASE_URL=
APP_BASE_URL=
TRACKING_BASE_URL=

SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

TRACKING_SIGNING_KEY=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=

PRIVACY_MODE=true
EVENT_RETENTION_DAYS=90

MAX_UPLOAD_MB=25
```

Do not commit secrets.

---

# 83. DEPLOYMENT

The system should be deployable with minimal cost.

Recommended conceptual layout:

```text
Supabase
   ├── Database
   ├── Auth
   ├── Storage
   └── Realtime

Free Python hosting
   └── FastAPI

Free/static hosting
   └── React dashboard

Brave
   └── Extension loaded manually during development
```

For the first version, it is acceptable to run FastAPI locally.

The architecture must support eventual public HTTPS deployment.

---

# 84. NO DOMAIN REQUIREMENT

The MVP must function without a custom domain.

Use:

```text
https://<host>/t/o/<token>
https://<host>/t/c/<token>
```

Later, configuration changes can move tracking to:

```text
https://track.example.com/t/o/<token>
```

Do not hard-code domains into the extension.

---

# 85. CHROME/BRAVE HOST PERMISSIONS

Only request permissions that are necessary.

Initial target:

```text
https://mail.google.com/*
```

plus your backend host.

Do not request:

```text
<all_urls>
```

unless a concrete feature absolutely requires it.

---

# 86. GMAIL DOM ROBUSTNESS

Gmail DOM is not a stable public API.

Therefore:

* centralize selectors;
* prefer semantic attributes;
* use MutationObserver carefully;
* avoid brittle class selectors;
* implement fallback selectors;
* add diagnostic mode;
* isolate Gmail-specific code from business logic;
* make selector changes require changing one module rather than the entire extension.

---

# 87. FAIL-SAFE BEHAVIOR

The extension must prioritize the user experience.

If anything goes wrong:

```text
tracking fails
→ email still sends
```

Examples:

* backend down;
* token request failed;
* tracking endpoint timeout;
* link signing failed;
* popup crashed;
* realtime disconnected.

Do not break Gmail's normal sending workflow.

---

# 88. FREE-TIER RESOURCE MANAGEMENT

Optimize aggressively for a single user.

Do:

```text
batch analytics queries
cache small datasets
avoid polling more than necessary
store only necessary metadata
use database indexes
paginate all lists
use signed URLs
delete expired documents/events
```

Do not:

```text
poll every second
stream every database row
run permanent workers
download mailbox continuously
store duplicate email bodies everywhere
```

---

# 89. PERFORMANCE TARGETS

Tracking endpoints should be extremely lightweight.

Target:

```text
p95 tracking endpoint < 300 ms
```

under ordinary free-tier conditions.

More important than absolute latency:

> do not make external API calls before returning the tracking pixel.

---

# 90. ANALYTICS QUERY STRATEGY

For a personal account, prioritize correctness over complicated warehouse architecture.

Use PostgreSQL queries/materialized summaries when useful.

Potential summary fields:

```text
open_count
unique_open_count
click_count
unique_click_count
reply_count
```

Do not prematurely introduce:

```text
ClickHouse
BigQuery
Kafka
data warehouse
```

---

# 91. DATABASE INDEXES

Create indexes for:

```text
tracked_emails(user_id, sent_at)
email_recipients(email)
email_recipients(tracked_email_id)
open_events(recipient_id, occurred_at)
click_events(recipient_id, occurred_at)
activity_events(user_id, occurred_at)
campaign_recipients(campaign_id)
campaign_recipients(contact_id)
contacts(user_id, email)
document_events(document_share_id, occurred_at)
```

Tune after observing actual queries.

---

# 92. SECURITY PRINCIPLE FOR TRACKING EVENTS

Anyone on the public internet can request a tracking URL.

Therefore:

```text
tracking URL
≠ authenticated API
```

The tracking endpoint itself must depend on an unforgeable capability token.

Never require a login to load the pixel.

---

# 93. PRIVACY PRINCIPLE

The system may collect personal data through tracking.

Therefore provide:

```text
data minimization
retention
erase
export
privacy settings
```

The personal project should not unnecessarily collect:

```text
full browsing history
complete email body archive
precise geolocation forever
raw UA forever
```

---

# 94. DO NOT STORE EMAIL CONTENT UNNECESSARILY

The system primarily needs:

```text
metadata
subject where useful
recipient
message ID
thread ID
tracking events
```

Do not create a full mailbox clone.

Only store message body content when a specific product feature genuinely needs it.

---

# 95. OPTIONAL AI LAYER

Design an interface:

```python
class AIService(Protocol):
    async def summarize_email(...)
    async def draft_followup(...)
    async def classify_contact(...)
    async def explain_engagement(...)
```

Do not make AI mandatory for MVP.

Potential future features:

```text
email summary
reply draft
follow-up draft
engagement explanation
contact classification
campaign copy
subject suggestions
```

Provider should be replaceable.

---

# 96. EMAIL PRODUCTIVITY INSIGHTS

Build reports that answer:

```text
How many emails did I send?
Which contacts engage most?
Who hasn't replied?
Which links are clicked?
When do people tend to open?
Which campaigns perform best?
Which PDFs are actually being viewed?
```

Do not infer causation from simple correlations.

---

# 97. INBOX / INCOMING TRACKING INDICATOR

A future enhancement may detect incoming emails that contain known tracking patterns.

Show:

```text
"Tracked email"
```

where technically reliable.

Do not claim detection is perfect.

---

# 98. ATTACHMENT CENTER

Store user-managed document metadata:

```text
filename
type
size
hash
created
linked email
contact
```

Do not silently ingest every Gmail attachment.

Only process files explicitly sent through the product.

---

# 99. PERSONAL PRODUCTIVITY FEATURES

Useful additions beyond strict Mailtrack parity:

```text
follow-up inbox
hot contacts
unopened queue
replied queue
waiting-on-me
waiting-on-them
recently revived
```

This is where the project can become more useful than a simple tracker.

---

# 100. WAITING-ON-THEM VIEW

Create a view:

```text
I sent an email
+
they have not replied
```

Sorted by:

```text
oldest waiting
highest engagement
hot conversation
follow-up due
```

This should become one of the most useful personal workflows.

---

# 101. WAITING-ON-ME VIEW

Detect:

```text
incoming message
+
I have not replied
```

This can become a lightweight email task list.

---

# 102. CRM ACTIVITY SCORE

Contacts can accumulate:

```text
engagement score
last activity
number of conversations
open frequency
click frequency
reply frequency
```

Do not turn this into a complicated sales CRM.

Keep it personal and actionable.

---

# 103. API IDENTITY MODEL

Every domain object should have:

```text
internal ID
public UUID
user ownership
timestamps
```

Never expose sequential database IDs in public tracking URLs.

---

# 104. ERROR HANDLING

Use consistent API responses.

Example:

```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "Invalid destination URL."
  }
}
```

Never expose:

* stack traces;
* SQL errors;
* secret configuration;
* internal security reasoning.

---

# 105. DEVELOPMENT PHASES

Build incrementally.

## PHASE 1 — Foundation

```text
FastAPI
Supabase
Auth
database
health endpoint
project structure
```

## PHASE 2 — Tracking Core

```text
tracked emails
recipient identity
open pixel
click redirects
tracking tokens
```

## PHASE 3 — Gmail Extension

```text
compose detection
send interception
pixel injection
link rewriting
checkmarks
```

## PHASE 4 — Dashboard

```text
activity
email detail
analytics
settings
```

## PHASE 5 — Realtime

```text
Supabase Realtime
desktop notification
activity updates
```

## PHASE 6 — Follow-up

```text
no reply
hot
revival
reminders
```

## PHASE 7 — Gmail API

```text
OAuth
message IDs
thread correlation
reply detection
```

## PHASE 8 — Contacts + Templates

```text
CRM
lists
notes
templates
```

## PHASE 9 — Campaigns

```text
mail merge
personalization
scheduling
campaign analytics
bounce/unsubscribe
```

## PHASE 10 — Documents

```text
PDF tracking
secure viewer
page analytics
download tracking
watermarks
```

## PHASE 11 — Professional Tools

```text
polls
video
eSignature
certificates
webhooks
```

## PHASE 12 — Intelligence

```text
engagement scores
automation engine
AI layer
productivity dashboards
```

---

# 106. MVP DEFINITION

Do NOT attempt the entire feature set in the first sprint.

MVP must include:

```text
Brave extension
Gmail compose integration
tracking toggle
open tracking
link tracking
signed URLs
checkmarks
activity dashboard
realtime notifications
Gmail account connection
reply correlation
no-reply reminders
contacts
templates
```

The MVP should be genuinely usable daily.

---

# 107. POST-MVP

After MVP is stable:

```text
campaigns
mail merge
scheduling
bounce detection
unsubscribe
PDF tracking
secure sharing
watermarks
polls
video
webhooks
eSignature
reports
automations
AI
```

---

# 108. DEFINITION OF DONE

The system is not considered complete merely because endpoints exist.

It is complete when a real user can:

1. open Gmail in Brave;
2. compose a message;
3. turn tracking on;
4. send;
5. open the message from a separate inbox;
6. see the open in the dashboard;
7. click a tracked link;
8. see the click;
9. receive the real-time notification;
10. reply;
11. see the reply correlated;
12. have the no-reply reminder stop;
13. inspect the whole activity timeline.

Then:

14. import contacts;
15. create a personalized campaign;
16. send individualized messages;
17. inspect recipient-level engagement;
18. upload a PDF;
19. send a secure tracked document;
20. inspect page-level analytics.

---

# 109. IMPLEMENTATION STYLE

Code should be:

* typed;
* modular;
* readable;
* documented where non-obvious;
* tested;
* secure by default;
* free-tier-conscious.

Use:

```text
Python type hints
Pydantic models
SQLAlchemy 2 style
async where beneficial
pytest
ruff
mypy where practical
```

Do not create unnecessary abstractions.

---

# 110. CODING AGENT BEHAVIOR

When implementing:

1. First inspect the repository.
2. Identify what already exists.
3. Do not overwrite working code blindly.
4. Create a dependency graph.
5. Implement in small vertical slices.
6. Run tests after each major slice.
7. Fix failures before proceeding.
8. Keep configuration centralized.
9. Keep Gmail DOM code isolated.
10. Keep tracking/security code isolated.
11. Never expose secrets.
12. Document setup commands.
13. Produce migrations.
14. Include seed/demo data where useful.
15. Keep the system runnable at every milestone.

---

# 111. IMPORTANT NON-GOALS

Do not initially build:

```text
enterprise multi-tenancy
billing
subscription plans
mobile apps
Outlook add-in
full Salesforce clone
marketing automation platform
mass-spam infrastructure
SMTP server
Kubernetes
microservices
distributed event bus
```

The goal is:

> the best possible personal Mailtrack/Mailsuite-style system with minimal infrastructure and no unnecessary recurring costs.

---

# 112. FINAL PRODUCT VISION

The final system should feel like:

```text
Gmail
+
Mailtrack
+
Mailsuite
+
lightweight CRM
+
follow-up manager
+
document analytics
+
personal email productivity dashboard
```

while remaining:

```text
single-user
personal
cheap/free-tier-first
Python-based
Supabase-powered
Brave-friendly
Gmail-native
modular
secure
maintainable
```

The priority hierarchy is:

```text
1. Reliable sending
2. Reliable tracking
3. Accurate event history
4. Excellent Gmail UX
5. Real-time activity
6. Follow-up intelligence
7. Contacts
8. Campaigns
9. Documents
10. Productivity automation
11. AI
```

Never sacrifice Gmail's ability to send mail merely to preserve tracking.

Never sacrifice security merely to make tracking easier.

Never claim an email was human-read when the evidence only shows that a resource was fetched.

Build the system incrementally, test each milestone against a real Gmail + Brave workflow, and favor the simplest free-tier-compatible implementation at every architectural decision.
