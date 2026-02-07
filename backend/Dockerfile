# ─── Build stage ────────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==2.3.2

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no dev, no root package)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# ─── Runtime stage ──────────────────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Note: When HF_API_TOKEN is set, embeddings use Hugging Face API (no local model needed)
# This saves memory on free tier hosting (512MB limit)

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
