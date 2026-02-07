"""FastAPI application entrypoint with lifespan, CORS, and router registration."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Request
from telegram import Update

from app.config import settings
from app.models import HealthResponse
from app.routers import chat, search, sections
from app.services.embeddings import load_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: load the embedding model and set up Telegram webhook on startup."""
    logger.info("Starting Tokyo Guide Backend...")
    load_model()

    # Set up Telegram bot webhook if token is configured
    if settings.telegram_bot_token:
        try:
            from app.telegram.bot import create_bot_application, setup_webhook

            bot_app = create_bot_application()
            await bot_app.initialize()
            await setup_webhook(bot_app)
            # Store bot app in FastAPI state for the webhook endpoint
            application.state.bot_app = bot_app
            logger.info("Telegram bot initialized")
        except Exception as e:
            logger.warning("Telegram bot setup failed (non-critical): %s", e)
    else:
        logger.info("TELEGRAM_BOT_TOKEN not set, Telegram bot disabled")

    logger.info("Application ready.")
    yield

    # Shutdown
    if hasattr(application.state, "bot_app"):
        await application.state.bot_app.shutdown()
    logger.info("Shutting down Tokyo Guide Backend.")


app = FastAPI(
    title="Tokyo Travel Guide API",
    description="RAG-powered Tokyo travel guide with chat, content browsing, and Telegram bot.",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────────────
# Allow the frontend origin, Vercel previews, and localhost for development
allowed_origins = [
    settings.frontend_url,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://tokyo-guide-pi.vercel.app",
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (safe for public API)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(sections.router)
app.include_router(search.router)


# ── Health check ────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for monitoring and deployment probes."""
    return HealthResponse(status="ok", version="0.1.0")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with basic info."""
    return {
        "name": "Tokyo Travel Guide API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# ── Telegram webhook ────────────────────────────────────────────────────────
@app.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> dict[str, str]:
    """Receive Telegram updates via webhook."""
    if not hasattr(request.app.state, "bot_app"):
        return {"status": "bot not initialized"}

    bot_app: "Application" = request.app.state.bot_app
    try:
        data = await request.json()
        update = Update.de_json(data, bot_app.bot)
        await bot_app.process_update(update)
    except Exception as e:
        logger.error("Error processing Telegram update: %s", e)

    return {"status": "ok"}
