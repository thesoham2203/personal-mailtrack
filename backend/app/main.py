"""FastAPI Main Application Entry Point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db


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

# Strict CORS configuration
origins = [
    "https://mail.google.com",
    settings.app_base_url,
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import (
    analytics,
    campaigns,
    contacts,
    diagnostics,
    documents,
    emails,
    templates,
    tracking,
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


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
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
    """Global exception handler to avoid leaking stack traces."""
    # Never leak internal database or system details to client
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please check server logs.",
            }
        },
    )
