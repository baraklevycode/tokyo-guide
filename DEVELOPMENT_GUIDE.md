# Tokyo Travel Guide - Development & Deployment Protocol

A comprehensive guide documenting the full development and deployment process of a RAG-powered travel guide application.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Prerequisites](#4-prerequisites)
5. [Local Development Setup](#5-local-development-setup)
6. [Database Setup (Supabase)](#6-database-setup-supabase)
7. [Backend Development](#7-backend-development)
8. [Frontend Development](#8-frontend-development)
9. [Content Scraping & Seeding](#9-content-scraping--seeding)
10. [Deployment](#10-deployment)
11. [Environment Variables](#11-environment-variables)
12. [Troubleshooting](#12-troubleshooting)
13. [Costs & Free Tiers](#13-costs--free-tiers)
14. [Lessons Learned](#14-lessons-learned)

---

## 1. Project Overview

### What We Built
A **RAG (Retrieval-Augmented Generation) powered travel guide** for Tokyo that:
- Answers questions about Tokyo in Hebrew and English
- Uses vector search to find relevant content from a blog
- Generates AI responses using Groq's free LLM API
- Displays content by categories (restaurants, hotels, neighborhoods, etc.)
- Works as a web app with a chat widget

### Data Sources
1. **Blog content**: Scraped from [ptitim.com/tokyoguide](https://www.ptitim.com/tokyoguide/) - a Hebrew Tokyo travel guide
2. **Map data**: Extracted from a Google My Maps KML file with 704 places

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                             │
│                    Next.js 15 + React                            │
│                    https://tokyo-guide-pi.vercel.app             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ API Calls
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Render)                              │
│                    FastAPI + Python                              │
│                    https://tokyo-guide.onrender.com              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  /api/chat   │  │ /api/sections│  │ /api/search  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              RAG Pipeline                            │        │
│  │  1. Embed question (HuggingFace API)                │        │
│  │  2. Vector search (Supabase pgvector)               │        │
│  │  3. Build context from results                       │        │
│  │  4. Generate answer (Groq API)                       │        │
│  └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   Hugging Face API      │    │      Groq API           │
│   (Embeddings)          │    │      (LLM)              │
│   FREE                  │    │      FREE               │
└─────────────────────────┘    └─────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE (Database)                           │
│                    PostgreSQL + pgvector                         │
│                    FREE tier                                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  tokyo_content table                                      │   │
│  │  - id, title, content (Hebrew)                           │   │
│  │  - category, tags, location                              │   │
│  │  - embedding (384-dim vector)                            │   │
│  │  - latitude, longitude (for map places)                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | REST API endpoints |
| Language | Python 3.10 | Backend logic |
| Package Manager | Poetry | Dependency management |
| Embeddings | sentence-transformers / HF API | Vector generation |
| LLM | Groq (openai/gpt-oss-20b) | Answer generation |
| Database | Supabase (PostgreSQL + pgvector) | Data storage & vector search |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 15 | React framework |
| Language | TypeScript | Type-safe frontend |
| Styling | Tailwind CSS | UI styling |
| Deployment | Vercel | Hosting |

### External Services (All Free)
| Service | Purpose | Free Tier Limits |
|---------|---------|------------------|
| Supabase | Database | 500MB storage, 2GB bandwidth |
| Groq | LLM API | ~30 requests/minute |
| Hugging Face | Embeddings API | ~30,000 requests/month |
| Render | Backend hosting | 750 hours/month, sleeps after 15min |
| Vercel | Frontend hosting | 100GB bandwidth/month |

---

## 4. Prerequisites

### Accounts Needed (All Free)
1. **GitHub** - https://github.com (for code repository)
2. **Supabase** - https://supabase.com (database)
3. **Groq** - https://console.groq.com (LLM API)
4. **Hugging Face** - https://huggingface.co (embeddings API)
5. **Render** - https://render.com (backend hosting)
6. **Vercel** - https://vercel.com (frontend hosting)

### Local Tools
- Python 3.10+
- Node.js 18+
- Git
- Poetry (`pip install poetry`)

---

## 5. Local Development Setup

### 5.1 Clone/Create Project Structure

```
japan-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          # Environment config
│   │   ├── main.py            # FastAPI app
│   │   ├── models.py          # Pydantic models
│   │   ├── routers/           # API endpoints
│   │   │   ├── chat.py
│   │   │   ├── search.py
│   │   │   └── sections.py
│   │   ├── services/          # Business logic
│   │   │   ├── database.py    # Supabase client
│   │   │   ├── embeddings.py  # Vector embeddings
│   │   │   ├── groq_client.py # LLM integration
│   │   │   └── rag.py         # RAG pipeline
│   │   └── telegram/          # Telegram bot (optional)
│   ├── scripts/               # Data seeding
│   │   ├── scrape_blog.py
│   │   ├── scrape_map.py
│   │   └── seed_database.py
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   ├── components/        # React components
│   │   └── lib/
│   │       └── api.ts         # API client
│   ├── package.json
│   └── .env.local
├── supabase/
│   └── schema.sql             # Database schema
└── .gitignore
```

### 5.2 Backend Setup

```bash
cd backend

# Install Poetry (if not installed)
pip install poetry

# Install dependencies
poetry install

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

### 5.3 Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 5.4 Run Locally

```bash
# Terminal 1: Backend
cd backend
poetry run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 6. Database Setup (Supabase)

### 6.1 Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - Name: `tokyo-guide`
   - Database Password: (save this!)
   - Region: Choose closest to you
4. Wait for project creation (~2 minutes)

### 6.2 Get API Keys

Go to **Settings → API**:
- **Project URL**: `https://xxxxx.supabase.co` → This is `SUPABASE_URL`
- **anon public key**: `eyJhbGc...` → This is `SUPABASE_KEY`

### 6.3 Run Database Schema

Go to **SQL Editor** and run:

```sql
-- Enable pgvector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Main content table
CREATE TABLE IF NOT EXISTS tokyo_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    title_hebrew TEXT,
    content TEXT,
    content_hebrew TEXT,
    category TEXT NOT NULL,
    subcategory TEXT,
    tags TEXT[] DEFAULT '{}',
    location_name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    price_range TEXT,
    recommended_duration TEXT,
    best_time_to_visit TEXT,
    embedding VECTOR(384),  -- 384 dimensions for multilingual model
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat sessions for conversation history
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    platform TEXT DEFAULT 'web',
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(384),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    title_hebrew TEXT,
    content TEXT,
    content_hebrew TEXT,
    category TEXT,
    subcategory TEXT,
    tags TEXT[],
    location_name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        tc.id,
        tc.title,
        tc.title_hebrew,
        tc.content,
        tc.content_hebrew,
        tc.category,
        tc.subcategory,
        tc.tags,
        tc.location_name,
        tc.latitude,
        tc.longitude,
        1 - (tc.embedding <=> query_embedding) AS similarity
    FROM tokyo_content tc
    WHERE 1 - (tc.embedding <=> query_embedding) > match_threshold
    ORDER BY tc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tokyo_content_category ON tokyo_content(category);
CREATE INDEX IF NOT EXISTS idx_tokyo_content_embedding ON tokyo_content 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 7. Backend Development

### 7.1 Key Files Explained

**`app/config.py`** - Environment configuration:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    hf_api_token: str = ""  # For Hugging Face API
    frontend_url: str = "http://localhost:3000"
    
    model_config = {"env_file": ".env"}

settings = Settings()
```

**`app/services/embeddings.py`** - Two modes:
1. **Local mode** (development): Loads sentence-transformers model locally
2. **API mode** (production): Uses Hugging Face Inference API (saves memory)

```python
# Checks HF_API_TOKEN to decide which mode
if HF_API_TOKEN:
    # Use Hugging Face API (low memory)
else:
    # Load local model (needs ~1GB RAM)
```

**`app/services/rag.py`** - The RAG pipeline:
```python
async def answer_question(question, session_id):
    # 1. Generate embedding for question
    embedding = encode_text(question)
    
    # 2. Vector search in Supabase
    results = vector_search(embedding, threshold=0.5, count=5)
    
    # 3. Build context from results
    context = format_results_as_context(results)
    
    # 4. Generate answer with Groq
    answer = generate_response(context, question)
    
    # 5. Generate follow-up suggestions
    suggestions = generate_suggested_questions(question, answer)
    
    return ChatResponse(answer, sources, session_id, suggestions)
```

### 7.2 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Send question, get AI answer |
| `/api/sections` | GET | Get all categories with counts |
| `/api/section/{category}` | GET | Get content for a category |
| `/api/search` | POST | Search content by query |
| `/health` | GET | Health check |

---

## 8. Frontend Development

### 8.1 Key Components

**`src/components/ChatWidget.tsx`** - The chat interface:
- Floating button in bottom-left corner
- Expandable chat panel
- Message history with user/assistant styling
- Suggested questions as clickable buttons
- Source references shown below answers

**`src/lib/api.ts`** - API client:
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendChatMessage(question: string, sessionId?: string) {
    const response = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, session_id: sessionId }),
    });
    return response.json();
}
```

### 8.2 RTL Support (Hebrew)

The app supports Hebrew with right-to-left text:
```tsx
<html dir="rtl" lang="he-IL">
```

---

## 9. Content Scraping & Seeding

### 9.1 Blog Scraper (`scripts/scrape_blog.py`)

**Problem encountered**: The blog returned compressed (gzip) content that wasn't properly decoded.

**Solution**: Remove `Accept-Encoding` header to get uncompressed HTML:
```python
headers = {
    "User-Agent": "Mozilla/5.0 ...",
    "Accept": "text/html,...",
    # Don't include Accept-Encoding to get plain HTML
}
```

**Content structure discovery**:
```python
# Used BeautifulSoup to analyze HTML structure
soup = BeautifulSoup(html, "lxml")

# Found content in: div.post__content (not div.entry-content)
content_area = soup.find("div", class_="post__content")

# Found 19 H2 headers representing major sections
h2s = content_area.find_all("h2")
```

### 9.2 Map Scraper (`scripts/scrape_map.py`)

Extracts places from Google My Maps KML:
```python
KML_URL = "https://www.google.com/maps/d/kml?mid=YOUR_MAP_ID&forcekml=1"

# Parse KML/XML
tree = ET.fromstring(kml_content)

# Extract places with coordinates
for placemark in tree.findall(".//Placemark"):
    name = placemark.find("name").text
    coords = placemark.find(".//coordinates").text  # "lng,lat,alt"
```

### 9.3 Database Seeding (`scripts/seed_database.py`)

```bash
# Run the seeding script
cd backend
poetry run python -m scripts.seed_database
```

What it does:
1. Clears existing content
2. Scrapes blog → 71 sections
3. Scrapes map → 704 places
4. Generates embeddings for all content
5. Inserts into Supabase

---

## 10. Deployment

### 10.1 Push to GitHub

```bash
# Initialize git
git init

# Create .gitignore (IMPORTANT - excludes secrets)
# .env, .env.local, node_modules/, __pycache__/, etc.

# Commit code
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then push
git remote add origin https://github.com/USERNAME/tokyo-guide.git
git branch -M main
git push -u origin main
```

### 10.2 Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js (auto-detected)
4. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
5. Deploy

### 10.3 Deploy Backend to Render

1. Go to https://dashboard.render.com/new/web-service
2. Connect GitHub repository
3. Configure:
   - **Name**: `tokyo-guide-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Instance Type**: `Free`
4. Add Environment Variables:
   - `GROQ_API_KEY` = your Groq key
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `HF_API_TOKEN` = your Hugging Face token
   - `FRONTEND_URL` = your Vercel URL
5. Deploy (takes 10-15 minutes first time)

### 10.4 Memory Issue & Fix

**Problem**: Render free tier has only 512MB RAM. Loading the sentence-transformers model locally requires ~1GB.

**Error seen**:
```
==> Out of memory (used over 512Mi)
```

**Solution**: Use Hugging Face Inference API instead of local model:

```python
# In embeddings.py - check for HF_API_TOKEN
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

if HF_API_TOKEN:
    # Use API (low memory) - call HuggingFace endpoint
    response = httpx.post(HF_API_URL, headers={"Authorization": f"Bearer {HF_API_TOKEN}"}, json={"inputs": texts})
else:
    # Use local model (high memory) - for development
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
```

---

## 11. Environment Variables

### Backend (.env)

```bash
# Groq API (free at console.groq.com)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Supabase (free at supabase.com)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...

# Hugging Face (free at huggingface.co/settings/tokens)
HF_API_TOKEN=hf_xxxxxxxxxxxxx

# Frontend URL (for CORS)
FRONTEND_URL=https://tokyo-guide-pi.vercel.app

# Optional: Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://tokyo-guide.onrender.com
```

---

## 12. Troubleshooting

### Issue: Blog scraper returns 0 sections

**Cause**: HTML was gzip-compressed and not decoded properly.

**Solution**: Remove `Accept-Encoding` header or let httpx handle decompression:
```python
# Don't include this header:
# "Accept-Encoding": "gzip, deflate, br"
```

### Issue: Wrong HTML selectors

**Cause**: Blog structure changed, `div.entry-content` doesn't exist.

**Solution**: Analyze actual HTML structure:
```python
soup = BeautifulSoup(html, "lxml")
# Check what classes exist
divs = soup.find_all("div", class_=True)
# Found: div.post__content instead of div.entry-content
```

### Issue: Render out of memory

**Cause**: sentence-transformers model needs >512MB RAM.

**Solution**: Use Hugging Face Inference API:
1. Get free token at https://huggingface.co/settings/tokens
2. Add `HF_API_TOKEN` to Render environment variables
3. Code checks for token and uses API instead of local model

### Issue: CORS errors

**Cause**: Backend doesn't allow frontend origin.

**Solution**: Add all Vercel URLs to CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific URLs
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Chat returns error

**Possible causes**:
1. HF API timeout (model warming up) - retry after a few seconds
2. Groq API rate limit - wait and retry
3. Supabase connection issue - check credentials

---

## 13. Costs & Free Tiers

| Service | Free Tier | Our Usage | Status |
|---------|-----------|-----------|--------|
| **Supabase** | 500MB DB, 2GB bandwidth | ~10MB, minimal | ✅ Well within |
| **Groq** | ~30 req/min, ~1000/day | Personal use | ✅ Well within |
| **Hugging Face** | ~30,000 req/month | ~100/day max | ✅ Well within |
| **Render** | 750 hours/month, 512MB RAM | Single instance | ✅ Well within |
| **Vercel** | 100GB bandwidth | Minimal | ✅ Well within |
| **GitHub** | Unlimited public repos | 1 repo | ✅ Well within |

**Total monthly cost: $0**

### Free Tier Limitations

1. **Render**: Server "sleeps" after 15 minutes of inactivity. First request takes ~30 seconds to wake up.

2. **Supabase**: Limited to 500MB. Our 775 items use ~10MB, so plenty of room.

3. **Groq**: Rate limited. Fine for personal use, may hit limits if shared widely.

---

## 14. Lessons Learned

### 1. Always Check HTML Structure First
Before writing scrapers, manually inspect the HTML:
```python
soup = BeautifulSoup(html, "lxml")
print(soup.find_all("div", class_=True)[:10])  # See what classes exist
```

### 2. Handle Encoding Properly
HTTP responses may be compressed. Either:
- Let the HTTP client handle it automatically
- Or explicitly request uncompressed content

### 3. Memory Constraints on Free Tiers
ML models are memory-hungry. Solutions:
- Use hosted inference APIs (HuggingFace, Replicate)
- Use smaller models
- Lazy load models only when needed

### 4. Security: Never Commit Secrets
Always use `.gitignore` to exclude:
```
.env
.env.local
*.pem
```

Verify before pushing:
```bash
git status  # Check what's being committed
```

### 5. CORS Must Be Configured
Backend must explicitly allow frontend origins:
```python
allow_origins=["https://your-frontend.vercel.app"]
```

### 6. Test Locally First
Always verify everything works locally before deploying:
```bash
# Backend
curl http://localhost:8000/api/sections

# Chat
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"question": "test"}'
```

### 7. Deployment Order Matters
1. Deploy database first (Supabase)
2. Seed data
3. Deploy backend (Render)
4. Deploy frontend (Vercel) - needs backend URL
5. Update frontend env vars with actual backend URL

---

## Quick Reference Commands

```bash
# Backend - Local Development
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 8000

# Backend - Run tests
poetry run pytest tests/

# Backend - Seed database
poetry run python -m scripts.seed_database

# Frontend - Local Development
cd frontend
npm install
npm run dev

# Git - Push changes
git add .
git commit -m "Your message"
git push

# Check API health
curl https://tokyo-guide.onrender.com/health
```

---

## URLs

| Service | URL |
|---------|-----|
| Frontend (Live) | https://tokyo-guide-pi.vercel.app |
| Backend (Live) | https://tokyo-guide.onrender.com |
| API Docs | https://tokyo-guide.onrender.com/docs |
| GitHub Repo | https://github.com/baraklevycode/tokyo-guide |
| Supabase Dashboard | https://supabase.com/dashboard |
| Render Dashboard | https://dashboard.render.com |
| Vercel Dashboard | https://vercel.com/dashboard |

---

*Document created: February 7, 2026*
*Last updated: February 7, 2026*
