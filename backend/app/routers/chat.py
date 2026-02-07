"""Chat router -- POST /api/chat endpoint for the RAG-powered Q&A."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.models import ChatRequest, ChatResponse
from app.services.rag import answer_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint. Accepts a question in Hebrew/English, retrieves relevant
    content via vector search, and generates an answer using Groq LLM.

    Returns the answer, source references, session ID, and suggested follow-up questions.
    """
    try:
        response = await answer_question(
            question=request.question,
            session_id=request.session_id,
            platform="web",
        )
        return response
    except Exception as e:
        logger.error("Chat endpoint error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="שגיאה בעיבוד השאלה. נסה שוב.")
