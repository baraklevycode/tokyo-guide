"""FastAPI application entrypoint with lifespan, CORS, and router registration."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    """Application lifespan: load the embedding model on startup."""
    logger.info("Starting Tokyo Guide Backend...")
    load_model()
    logger.info("Application ready.")
    yield
    logger.info("Shutting down Tokyo Guide Backend.")


app = FastAPI(
    title="Tokyo Travel Guide API",
    description="RAG-powered Tokyo travel guide with chat and content browsing.",
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
