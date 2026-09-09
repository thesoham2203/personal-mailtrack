"""Application configuration using Pydantic Settings."""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment & URLs
    app_env: str = Field(default="development", alias="APP_ENV")
    api_base_url: str = Field(default="http://localhost:8000", alias="API_BASE_URL")
    tracking_base_url: str = Field(default="http://localhost:8000", alias="TRACKING_BASE_URL")
    app_base_url: str = Field(default="http://localhost:5173", alias="APP_BASE_URL")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./mailtrack.db",
        alias="DATABASE_URL",
    )
    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: str | None = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str | None = Field(
        default=None, alias="SUPABASE_SERVICE_ROLE_KEY"
    )

    # Security & Tokens
    tracking_signing_key: str = Field(
        default="dev-tracking-secret-key-32-chars-minimum!!",
        alias="TRACKING_SIGNING_KEY",
    )
    tracking_previous_keys: list[str] = Field(default_factory=list, alias="TRACKING_PREVIOUS_KEYS")
    encryption_key: str | None = Field(default=None, alias="ENCRYPTION_KEY")

    # Google OAuth
    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/gmail/oauth/callback",
        alias="GOOGLE_REDIRECT_URI",
    )

    # Privacy & Limits
    privacy_mode: bool = Field(default=True, alias="PRIVACY_MODE")
    event_retention_days: int = Field(default=90, alias="EVENT_RETENTION_DAYS")
    tracking_prepare_timeout_ms: int = Field(default=2500, alias="TRACKING_PREPARE_TIMEOUT_MS")
    max_upload_mb: int = Field(default=25, alias="MAX_UPLOAD_MB")

    # Feature Flags
    demo_mode: bool = Field(default=False, alias="DEMO_MODE")
    feature_campaigns: bool = Field(default=True, alias="FEATURE_CAMPAIGNS")
    feature_documents: bool = Field(default=True, alias="FEATURE_DOCUMENTS")
    feature_signatures: bool = Field(default=True, alias="FEATURE_SIGNATURES")
    feature_polls: bool = Field(default=True, alias="FEATURE_POLLS")
    feature_video: bool = Field(default=True, alias="FEATURE_VIDEO")
    feature_webhooks: bool = Field(default=True, alias="FEATURE_WEBHOOKS")
    feature_ai: bool = Field(default=False, alias="FEATURE_AI")


settings = Settings()
