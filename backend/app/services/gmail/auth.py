"""Gmail OAuth helpers - credential-gated."""

from app.config import settings


def is_gmail_api_enabled() -> bool:
    """Returns True if Gmail API credentials are configured."""
    return bool(settings.google_client_id and settings.google_client_secret)


def get_oauth_authorization_url(gmail_account_id: str) -> str | None:
    """Build and return Google OAuth2 authorization URL, or None if not configured."""
    if not is_gmail_api_enabled():
        return None
    scope = "https://www.googleapis.com/auth/gmail.readonly"
    redirect_uri = settings.google_redirect_uri or f"{settings.api_base_url}/api/v1/gmail/callback"
    return (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&state={gmail_account_id}"
    )


async def exchange_code_for_tokens(code: str) -> dict | None:
    """Exchange authorization code for access + refresh tokens."""
    if not is_gmail_api_enabled():
        return None
    import httpx

    redirect_uri = settings.google_redirect_uri or f"{settings.api_base_url}/api/v1/gmail/callback"
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        r.raise_for_status()
        return r.json()
