"""Groq API client wrapper for LLM chat completions using openai/gpt-oss-20b."""

from __future__ import annotations

import logging
from typing import Optional

from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)

# Singleton client
_client: Optional[Groq] = None

# System prompt for the Tokyo travel guide assistant
SYSTEM_PROMPT_TEMPLATE = """אתה מדריך טיולים מומחה לטוקיו, יפן. אתה עונה על שאלות בעברית בצורה ידידותית, מדויקת ומפורטת.

השתמש במידע הבא כדי לענות על שאלות המשתמש:

{context}

הנחיות:
1. ענה תמיד בעברית, אלא אם המשתמש שואל באנגלית.
2. ציין שמות מקומות גם באנגלית (באותיות לטיניות) לצד העברית, לנוחות ניווט.
3. תן תשובות ברורות, מדויקות ומועילות על בסיס המידע שקיבלת.
4. אם המידע לא מופיע בהקשר שקיבלת, אמור זאת בכנות ונסה לתת עצה כללית.
5. כשממליץ על מסעדות או מקומות, ציין גם את האזור/שכונה.
6. היה חם ומזמין, כמו חבר שמכיר את טוקיו היטב.
7. אם המשתמש שואל על מחירים, ציין ביין יפני (¥) וגם הערכה בשקלים.
"""


def get_groq_client() -> Groq:
    """Get or create the Groq client singleton."""
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY must be set in environment variables")
        _client = Groq(api_key=settings.groq_api_key)
        logger.info("Groq client initialized (model: %s)", settings.groq_model_name)
    return _client


def generate_response(
    context: str,
    question: str,
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    """
    Generate a response using Groq's openai/gpt-oss-20b reasoning model.

    The model streams reasoning tokens first (chain-of-thought), then content tokens.
    We use non-streaming mode here since we return a JSON response, not a stream.

    Args:
        context: Relevant content retrieved from the vector database.
        question: The user's question.
        chat_history: Optional list of previous messages.

    Returns:
        The generated answer text.
    """
    client = get_groq_client()

    system_message = SYSTEM_PROMPT_TEMPLATE.format(context=context if context else "אין מידע ספציפי זמין.")

    messages = [{"role": "system", "content": system_message}]

    # Add chat history (keep last 6 messages to stay within context limits)
    if chat_history:
        messages.extend(chat_history[-6:])

    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model=settings.groq_model_name,
            messages=messages,
            temperature=settings.rag_temperature,
            max_completion_tokens=settings.rag_max_completion_tokens,
            top_p=settings.rag_top_p,
            reasoning_effort=settings.rag_reasoning_effort,
            stream=False,
            stop=None,
        )
        answer = response.choices[0].message.content
        return answer or "מצטער, לא הצלחתי ליצור תשובה. נסה שוב."
    except Exception as e:
        logger.error("Groq API call failed: %s", e)
        return "מצטער, אירעה שגיאה בעיבוד השאלה. נסה שוב בעוד רגע."


def generate_suggested_questions(question: str, answer: str) -> list[str]:
    """
    Generate follow-up question suggestions based on the conversation.

    Returns a list of 3 suggested questions in Hebrew.
    """
    client = get_groq_client()

    try:
        response = client.chat.completions.create(
            model=settings.groq_model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "אתה עוזר ליצור שאלות המשך. בהינתן שאלה ותשובה על טוקיו, "
                        "צור בדיוק 3 שאלות המשך קצרות ורלוונטיות בעברית. "
                        "החזר רק את השאלות, כל אחת בשורה חדשה, ללא מספור."
                    ),
                },
                {"role": "user", "content": f"שאלה: {question}\n\nתשובה: {answer}"},
            ],
            temperature=settings.rag_temperature,
            max_completion_tokens=512,
            top_p=settings.rag_top_p,
            reasoning_effort=settings.rag_reasoning_effort,
            stream=False,
            stop=None,
        )
        raw = response.choices[0].message.content or ""
        suggestions = [line.strip() for line in raw.strip().split("\n") if line.strip()]
        return suggestions[:3]
    except Exception as e:
        logger.error("Failed to generate suggestions: %s", e)
        return [
            "מה כדאי לאכול בטוקיו?",
            "איך להתניידד בתחבורה ציבורית?",
            "אילו שכונות מומלצות לביקור?",
        ]
