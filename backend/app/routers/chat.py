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
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            raise HTTPException(status_code=504, detail="השירות עמוס. נסה שוב בעוד רגע.")
        elif "HF API" in error_msg or "embedding" in error_msg.lower():
            raise HTTPException(status_code=503, detail="שירות ה-AI זמנית לא זמין. נסה שוב.")
        elif "groq" in error_msg.lower():
            raise HTTPException(status_code=503, detail="שירות השפה זמנית לא זמין. נסה שוב.")
        raise HTTPException(status_code=500, detail="שגיאה בעיבוד השאלה. נסה שוב.")
