"""RAG (Retrieval-Augmented Generation) pipeline for the Tokyo Guide chatbot."""

from __future__ import annotations

import logging
from typing import Optional

from app.config import settings
from app.models import ChatResponse, SourceReference
from app.services.database import (
    create_session,
    get_session,
    update_session_messages,
    vector_search,
)
from app.services.embeddings import encode_text
from app.services.groq_client import generate_response, generate_suggested_questions

logger = logging.getLogger(__name__)


async def answer_question(
    question: str,
    session_id: Optional[str] = None,
    platform: str = "web",
    user_id: str = "anonymous",
) -> ChatResponse:
    """
    Full RAG pipeline: embed question -> vector search -> build context -> generate answer.

    Args:
        question: The user's question in Hebrew or English.
        session_id: Optional existing session ID for conversation continuity.
        platform: Client platform identifier (default 'web').
        user_id: User identifier (default 'anonymous').

    Returns:
        ChatResponse with answer, sources, session_id, and suggested questions.
    """
    # 1. Generate embedding for the question
    logger.info("Processing question: %s", question[:80])
    question_embedding = encode_text(question)

    # 2. Search for similar content in the database
    search_results = vector_search(
        query_embedding=question_embedding,
        match_threshold=settings.rag_match_threshold,
        match_count=settings.rag_match_count,
    )

    # 3. Build context from search results (128K context allows full content)
    max_content_per_source = 2000  # Generous limit per source with 128K context window
    context_parts = []
    sources = []
    for result in search_results:
        title_heb = result.get("title_hebrew", "")
        content_heb = result.get("content_hebrew", "")
        if len(content_heb) > max_content_per_source:
            content_heb = content_heb[:max_content_per_source] + "..."
        context_parts.append(f"## {title_heb}\n{content_heb}")

        sources.append(
            SourceReference(
                id=str(result.get("id", "")),
                title=result.get("title", ""),
                title_hebrew=title_heb,
                category=result.get("category", ""),
                similarity=round(result.get("similarity", 0.0), 3),
            )
        )

    context = "\n\n---\n\n".join(context_parts) if context_parts else ""

    # 4. Get or create session for chat history
    if session_id:
        session = get_session(session_id)
        if session:
            chat_history = session.get("messages", [])
        else:
            # Session not found, create a new one
            session_id = create_session(user_id=user_id, platform=platform)
            chat_history = []
    else:
        session_id = create_session(user_id=user_id, platform=platform)
        chat_history = []

    # 5. Generate answer using Groq
    answer = generate_response(
        context=context,
        question=question,
        chat_history=chat_history,
    )

    # 6. Generate suggested follow-up questions
    suggested = generate_suggested_questions(question, answer)

    # 7. Save conversation to session
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": answer})
    # Keep only the last 10 messages to avoid growing too large
    chat_history = chat_history[-10:]
    update_session_messages(session_id, chat_history)

    return ChatResponse(
        answer=answer,
        sources=sources,
        session_id=session_id,
        suggested_questions=suggested,
    )
