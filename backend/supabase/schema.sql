-- Supabase PostgreSQL Schema for Personal Mailtrack / Mailsuite-Style Suite
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- 1. Profiles
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email CITEXT UNIQUE NOT NULL,
    display_name TEXT,
    timezone TEXT DEFAULT 'UTC' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 2. Gmail Accounts (Multiple personal accounts)
CREATE TABLE IF NOT EXISTS gmail_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    google_account_id TEXT,
    email CITEXT NOT NULL,
    display_name TEXT,
    picture_url TEXT,
    is_default BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 3. OAuth Credentials (Server-side encrypted)
CREATE TABLE IF NOT EXISTS oauth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gmail_account_id UUID REFERENCES gmail_accounts(id) ON DELETE CASCADE UNIQUE NOT NULL,
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT NOT NULL,
    expires_at TIMESTAMPTZ,
    scopes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 4. Tracked Emails (Parent email)
CREATE TABLE IF NOT EXISTS tracked_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    gmail_account_id UUID REFERENCES gmail_accounts(id) ON DELETE SET NULL,
    public_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    gmail_message_id TEXT,
    gmail_thread_id TEXT,
    rfc_message_id TEXT,
    subject TEXT,
    snippet TEXT,
    campaign_id UUID,
    sent_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 5. Email Recipients (Individual recipient delivery identity)
CREATE TABLE IF NOT EXISTS email_recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracked_email_id UUID REFERENCES tracked_emails(id) ON DELETE CASCADE NOT NULL,
    contact_id UUID,
    email CITEXT NOT NULL,
    name TEXT,
    recipient_type TEXT DEFAULT 'to' NOT NULL,
    tracking_token_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    first_open_at TIMESTAMPTZ,
    last_open_at TIMESTAMPTZ,
    first_click_at TIMESTAMPTZ,
    last_click_at TIMESTAMPTZ,
    raw_open_count INTEGER DEFAULT 0 NOT NULL,
    human_open_count INTEGER DEFAULT 0 NOT NULL,
    human_click_count INTEGER DEFAULT 0 NOT NULL,
    reply_received_at TIMESTAMPTZ,
    bounced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 6. Tracked Links
CREATE TABLE IF NOT EXISTS tracked_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracked_email_id UUID REFERENCES tracked_emails(id) ON DELETE CASCADE NOT NULL,
    original_url TEXT NOT NULL,
    normalized_url TEXT NOT NULL,
    link_text TEXT,
    position INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 7. Open Events (Raw tracking events with bot classification)
CREATE TABLE IF NOT EXISTS open_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID REFERENCES email_recipients(id) ON DELETE CASCADE NOT NULL,
    occurred_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    client_name TEXT,
    os_name TEXT,
    device_type TEXT,
    country TEXT,
    region TEXT,
    city TEXT,
    classification TEXT DEFAULT 'unknown' NOT NULL,
    confidence REAL DEFAULT 0.5 NOT NULL,
    classification_reason TEXT
);

-- 8. Click Events
CREATE TABLE IF NOT EXISTS click_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID REFERENCES email_recipients(id) ON DELETE CASCADE NOT NULL,
    tracked_link_id UUID REFERENCES tracked_links(id) ON DELETE SET NULL,
    destination_url TEXT NOT NULL,
    occurred_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    classification TEXT DEFAULT 'human_likely' NOT NULL,
    confidence REAL DEFAULT 1.0 NOT NULL
);

-- 9. Reply Events
CREATE TABLE IF NOT EXISTS reply_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID REFERENCES email_recipients(id) ON DELETE CASCADE NOT NULL,
    gmail_message_id TEXT,
    rfc_message_id TEXT,
    in_reply_to TEXT,
    subject TEXT,
    snippet TEXT,
    received_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 10. Bounce Events
CREATE TABLE IF NOT EXISTS bounce_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID REFERENCES email_recipients(id) ON DELETE CASCADE NOT NULL,
    bounce_type TEXT DEFAULT 'hard' NOT NULL,
    smtp_code TEXT,
    diagnostic_code TEXT,
    occurred_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 11. Universal Activity Events Timeline
CREATE TABLE IF NOT EXISTS activity_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    event_type TEXT NOT NULL,
    source TEXT DEFAULT 'tracking_engine' NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    occurred_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    metadata_json JSONB
);

-- 12. Contacts CRM
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    email CITEXT NOT NULL,
    name TEXT,
    company TEXT,
    phone TEXT,
    tags TEXT,
    notes TEXT,
    engagement_score INTEGER DEFAULT 0 NOT NULL,
    status TEXT DEFAULT 'Warm' NOT NULL,
    last_contacted_at TIMESTAMPTZ,
    last_opened_at TIMESTAMPTZ,
    last_clicked_at TIMESTAMPTZ,
    last_replied_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE (user_id, email)
);

CREATE TABLE IF NOT EXISTS contact_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS contact_list_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_list_id UUID REFERENCES contact_lists(id) ON DELETE CASCADE NOT NULL,
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE (contact_list_id, contact_id)
);

CREATE TABLE IF NOT EXISTS contact_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 13. Campaigns & Mail Merge
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    gmail_account_id UUID REFERENCES gmail_accounts(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    status TEXT DEFAULT 'draft' NOT NULL,
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    batch_size INTEGER DEFAULT 10 NOT NULL,
    delay_seconds INTEGER DEFAULT 5 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS campaign_recipients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE NOT NULL,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    email CITEXT NOT NULL,
    personalized_data JSONB,
    status TEXT DEFAULT 'pending' NOT NULL,
    tracked_email_id UUID REFERENCES tracked_emails(id) ON DELETE SET NULL,
    sent_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 14. Email Templates
CREATE TABLE IF NOT EXISTS email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    category TEXT,
    is_favorite BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 15. Documents & PDF Tracking
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT DEFAULT 'application/pdf' NOT NULL,
    sha256_hash TEXT NOT NULL,
    total_pages INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS document_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE NOT NULL,
    share_token TEXT UNIQUE NOT NULL,
    recipient_email CITEXT,
    recipient_name TEXT,
    expires_at TIMESTAMPTZ,
    password_hash TEXT,
    download_allowed BOOLEAN DEFAULT TRUE NOT NULL,
    watermark_text TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS document_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_share_id UUID REFERENCES document_shares(id) ON DELETE CASCADE NOT NULL,
    event_type TEXT DEFAULT 'page_view' NOT NULL,
    page_number INTEGER,
    duration_seconds REAL DEFAULT 0.0 NOT NULL,
    occurred_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    ip_address TEXT,
    user_agent TEXT
);

-- 16. Automations & Webhooks
CREATE TABLE IF NOT EXISTS automation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    event_trigger TEXT NOT NULL,
    conditions_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    actions_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS automation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID REFERENCES automation_rules(id) ON DELETE CASCADE NOT NULL,
    activity_event_id UUID NOT NULL,
    executed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    status TEXT DEFAULT 'success' NOT NULL,
    output_details TEXT
);

CREATE TABLE IF NOT EXISTS webhook_endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    url TEXT NOT NULL,
    secret TEXT NOT NULL,
    subscribed_events TEXT DEFAULT 'email.opened,email.clicked,email.replied' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES webhook_endpoints(id) ON DELETE CASCADE NOT NULL,
    event_id UUID NOT NULL,
    attempt_number INTEGER DEFAULT 1 NOT NULL,
    status_code INTEGER,
    delivered_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    success BOOLEAN DEFAULT FALSE NOT NULL,
    response_body TEXT
);

-- 17. Notification Rules & Events
CREATE TABLE IF NOT EXISTS notification_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    rule_type TEXT NOT NULL,
    channel TEXT DEFAULT 'desktop' NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    cooldown_minutes INTEGER DEFAULT 10 NOT NULL,
    conditions_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    rule_id UUID REFERENCES notification_rules(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    channel TEXT DEFAULT 'desktop' NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 18. Polls
CREATE TABLE IF NOT EXISTS polls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    question TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS poll_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    poll_id UUID REFERENCES polls(id) ON DELETE CASCADE NOT NULL,
    option_text TEXT NOT NULL,
    position INTEGER DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS poll_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    poll_id UUID REFERENCES polls(id) ON DELETE CASCADE NOT NULL,
    option_id UUID REFERENCES poll_options(id) ON DELETE CASCADE NOT NULL,
    recipient_email CITEXT,
    responded_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 19. User Settings
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE UNIQUE NOT NULL,
    privacy_mode BOOLEAN DEFAULT TRUE NOT NULL,
    store_ip_address BOOLEAN DEFAULT FALSE NOT NULL,
    store_user_agent BOOLEAN DEFAULT TRUE NOT NULL,
    desktop_notifications BOOLEAN DEFAULT TRUE NOT NULL,
    sound_notifications BOOLEAN DEFAULT FALSE NOT NULL,
    no_reply_threshold_hours INTEGER DEFAULT 48 NOT NULL,
    hot_conversation_opens INTEGER DEFAULT 3 NOT NULL,
    hot_conversation_window_minutes INTEGER DEFAULT 30 NOT NULL,
    revival_threshold_days INTEGER DEFAULT 7 NOT NULL,
    custom_settings_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- =========================================================================
-- Performance Indexes (PRD Section 91)
-- =========================================================================
CREATE INDEX IF NOT EXISTS ix_tracked_emails_user_sent ON tracked_emails(user_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS ix_recipients_email_created ON email_recipients(email, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_recipients_tracked_email ON email_recipients(tracked_email_id);
CREATE INDEX IF NOT EXISTS ix_recipients_token ON email_recipients(tracking_token_id);
CREATE INDEX IF NOT EXISTS ix_open_events_recip_occurred ON open_events(recipient_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS ix_click_events_recip_occurred ON click_events(recipient_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS ix_activity_events_user_occurred ON activity_events(user_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS ix_campaign_recipients_campaign ON campaign_recipients(campaign_id, status);
CREATE INDEX IF NOT EXISTS ix_contacts_user_email ON contacts(user_id, email);
CREATE INDEX IF NOT EXISTS ix_doc_events_share_occurred ON document_events(document_share_id, occurred_at DESC);

-- =========================================================================
-- Row Level Security (RLS) Policies (PRD Section 71)
-- =========================================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own profile" ON profiles
    FOR ALL USING (auth.uid() = id);

ALTER TABLE gmail_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own gmail accounts" ON gmail_accounts
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE tracked_emails ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own tracked emails" ON tracked_emails
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE email_recipients ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view recipients of own emails" ON email_recipients
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM tracked_emails te
            WHERE te.id = email_recipients.tracked_email_id AND te.user_id = auth.uid()
        )
    );

ALTER TABLE tracked_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view links of own emails" ON tracked_links
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM tracked_emails te
            WHERE te.id = tracked_links.tracked_email_id AND te.user_id = auth.uid()
        )
    );

ALTER TABLE open_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view opens of own emails" ON open_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM email_recipients er
            JOIN tracked_emails te ON te.id = er.tracked_email_id
            WHERE er.id = open_events.recipient_id AND te.user_id = auth.uid()
        )
    );

ALTER TABLE click_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view clicks of own emails" ON click_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM email_recipients er
            JOIN tracked_emails te ON te.id = er.tracked_email_id
            WHERE er.id = click_events.recipient_id AND te.user_id = auth.uid()
        )
    );

ALTER TABLE activity_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own activity events" ON activity_events
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own contacts" ON contacts
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE contact_lists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own contact lists" ON contact_lists
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own campaigns" ON campaigns
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own email templates" ON email_templates
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own documents" ON documents
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE automation_rules ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own automation rules" ON automation_rules
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE webhook_endpoints ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own webhook endpoints" ON webhook_endpoints
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE notification_rules ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own notification rules" ON notification_rules
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE notification_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own notification events" ON notification_events
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE polls ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own polls" ON polls
    FOR ALL USING (auth.uid() = user_id);

ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own settings" ON user_settings
    FOR ALL USING (auth.uid() = user_id);
