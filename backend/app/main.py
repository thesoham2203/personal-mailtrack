"""FastAPI Main Application Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    await init_db()
    yield


app = FastAPI(
    title="Personal Mailtrack API",
    description="Clean-room, personal-use Gmail email productivity & tracking suite.",
    version="0.1.0",
    lifespan=lifespan,
)

# Comprehensive CORS configuration supporting Gmail Web, Cloudflare Pages, local dev, and Chrome extensions
origins = [
    "https://mail.google.com",
    "https://personal-mailtrack.pages.dev",
    "https://personal-mailtrack-api.onrender.com",
    settings.app_base_url,
    settings.api_base_url,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^(chrome-extension://.*|https://.*\.pages\.dev|https://mail\.google\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import (
    analytics,
    auth,
    automations,
    campaigns,
    contacts,
    diagnostics,
    documents,
    emails,
    followup,
    gmail,
    notifications,
    templates,
    tracking,
    webhooks,
)

# Mount public tracking routes (/t/o, /t/c, /u, /d) and API routes
app.include_router(tracking.router)
app.include_router(documents.router)
app.include_router(emails.router)
app.include_router(contacts.router)
app.include_router(campaigns.router)
app.include_router(templates.router)
app.include_router(analytics.router)
app.include_router(diagnostics.router)
app.include_router(auth.router)
app.include_router(gmail.router)
app.include_router(followup.router)
app.include_router(notifications.router)
app.include_router(automations.router)
app.include_router(webhooks.router)


@app.api_route("/health", methods=["GET", "HEAD"], tags=["System"])
@app.api_route("/", methods=["GET", "HEAD"], tags=["System"])
async def health_check():
    """Health check endpoint supporting GET and HEAD for monitoring tools."""
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "database": "sqlite" if "sqlite" in settings.database_url else "postgresql",
        "demo_mode": settings.demo_mode,
        "features": {
            "campaigns": settings.feature_campaigns,
            "documents": settings.feature_documents,
            "signatures": settings.feature_signatures,
            "polls": settings.feature_polls,
            "video": settings.feature_video,
            "webhooks": settings.feature_webhooks,
            "ai": settings.feature_ai,
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log errors and avoid leaking internal details."""
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": f"An unexpected error occurred: {type(exc).__name__} - {str(exc)}",
            }
        },
    )
