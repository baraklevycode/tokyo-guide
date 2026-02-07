"""
Telegram bot for the Tokyo Travel Guide.

Provides the same RAG-powered Q&A as the web chat, plus command-based navigation.
Integrates with FastAPI via webhook (no long-polling needed).

Commands:
  /start    - Welcome message
  /help     - List available commands
  /sections - Browse content by category
  /search   - Search for content
  /itinerary - Get itinerary suggestions
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.services.database import get_content_by_category, keyword_search
from app.services.rag import answer_question

logger = logging.getLogger(__name__)

# Category metadata for inline keyboards
CATEGORIES = [
    ("neighborhoods", "שכונות ואזורים"),
    ("attractions", "אטרקציות וציוני דרך"),
    ("restaurants", "מסעדות ואוכל"),
    ("hotels", "מלונות ולינה"),
    ("transportation", "תחבורה"),
    ("shopping", "קניות"),
    ("cultural_experiences", "חוויות תרבותיות"),
    ("day_trips", "טיולי יום"),
    ("practical_tips", "טיפים שימושיים"),
]

# Telegram bot application (initialized lazily)
_bot_app: Optional[Application] = None


async def start_command(update: Update, context) -> None:
    """Handle /start command -- welcome message."""
    if not update.message:
        return
    await update.message.reply_text(
        "שלום! אני הבוט של מדריך טוקיו.\n\n"
        "שאל אותי כל שאלה על טוקיו - מסעדות, אטרקציות, מלונות, תחבורה ועוד!\n\n"
        "פקודות זמינות:\n"
        "/sections - עיון לפי קטגוריות\n"
        "/search <מילת חיפוש> - חיפוש חופשי\n"
        "/itinerary <מספר ימים> - הצעה למסלול\n"
        "/help - עזרה\n\n"
        "או פשוט שלח שאלה בעברית או באנגלית!",
        parse_mode=None,
    )


async def help_command(update: Update, context) -> None:
    """Handle /help command."""
    if not update.message:
        return
    await update.message.reply_text(
        "איך להשתמש בבוט:\n\n"
        "1. שלח שאלה בעברית או באנגלית ואקבל תשובה מפורטת\n"
        "2. /sections - עיון בתוכן לפי קטגוריות\n"
        "3. /search <מילה> - חיפוש תוכן לפי מילות מפתח\n"
        "4. /itinerary <ימים> - הצעה למסלול טיול\n\n"
        "דוגמאות לשאלות:\n"
        '- "מה כדאי לאכול בשיבויה?"\n'
        '- "איפה הכי כדאי לישון בטוקיו?"\n'
        '- "איך עובד המטרו?"\n'
        '- "המלצות לראמן טוב"',
        parse_mode=None,
    )


async def sections_command(update: Update, context) -> None:
    """Handle /sections command -- show category keyboard."""
    if not update.message:
        return

    keyboard = []
    for cat_id, cat_label in CATEGORIES:
        keyboard.append([InlineKeyboardButton(cat_label, callback_data=f"cat_{cat_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("בחר קטגוריה:", reply_markup=reply_markup)


async def search_command(update: Update, context) -> None:
    """Handle /search <query> command."""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text("שימוש: /search <מילת חיפוש>\nדוגמה: /search ראמן")
        return

    query = " ".join(context.args)
    results = keyword_search(query)

    if not results:
        await update.message.reply_text(f"לא נמצאו תוצאות עבור: {query}")
        return

    response_text = f"תוצאות חיפוש עבור \"{query}\":\n\n"
    for i, item in enumerate(results[:10], 1):
        title = item.get("title_hebrew", item.get("title", ""))
        response_text += f"{i}. {title}\n"

    await update.message.reply_text(response_text, parse_mode=None)


async def itinerary_command(update: Update, context) -> None:
    """Handle /itinerary <days> command -- generate itinerary via RAG."""
    if not update.message:
        return

    days = 3  # Default
    if context.args:
        try:
            days = int(context.args[0])
            days = max(1, min(days, 14))  # Clamp between 1-14
        except ValueError:
            pass

    question = f"תכנן לי מסלול טיול בן {days} ימים בטוקיו. תן המלצות ספציפיות לכל יום כולל מסעדות ואטרקציות."
    user_id = str(update.effective_user.id) if update.effective_user else "anonymous"

    await update.message.reply_text("מכין לך מסלול טיול... נא להמתין.")

    try:
        response = await answer_question(
            question=question,
            platform="telegram",
            user_id=user_id,
        )
        await update.message.reply_text(response.answer, parse_mode=None)
    except Exception as e:
        logger.error("Itinerary generation failed: %s", e)
        await update.message.reply_text("מצטער, אירעה שגיאה ביצירת המסלול. נסה שוב.")


async def handle_callback_query(update: Update, context) -> None:
    """Handle inline keyboard button presses (category selection)."""
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data or ""

    if data.startswith("cat_"):
        category = data[4:]  # Remove "cat_" prefix

        # Find the Hebrew label
        cat_label = category
        for cat_id, label in CATEGORIES:
            if cat_id == category:
                cat_label = label
                break

        items = get_content_by_category(category)

        if not items:
            await query.edit_message_text(f"אין תוכן זמין בקטגוריה: {cat_label}")
            return

        response_text = f"📌 {cat_label}:\n\n"
        for i, item in enumerate(items[:15], 1):
            title = item.get("title_hebrew", item.get("title", ""))
            content = item.get("content_hebrew", "")[:100]
            response_text += f"{i}. *{title}*\n{content}...\n\n"

        # Trim to Telegram message limit (4096 chars)
        if len(response_text) > 4000:
            response_text = response_text[:4000] + "\n\n... (יש עוד תוצאות)"

        try:
            await query.edit_message_text(response_text, parse_mode="Markdown")
        except Exception:
            # Fallback without markdown if parsing fails
            await query.edit_message_text(response_text, parse_mode=None)


async def handle_text_message(update: Update, context) -> None:
    """Handle free-text messages -- pass to RAG pipeline."""
    if not update.message or not update.message.text:
        return

    user_message = update.message.text
    user_id = str(update.effective_user.id) if update.effective_user else "anonymous"

    try:
        response = await answer_question(
            question=user_message,
            platform="telegram",
            user_id=user_id,
        )

        # Build response with sources
        answer_text = response.answer

        if response.sources:
            answer_text += "\n\n📚 מקורות:"
            for source in response.sources[:3]:
                answer_text += f"\n• {source.title_hebrew}"

        # Add suggested questions as inline keyboard
        keyboard = []
        for suggestion in response.suggested_questions[:3]:
            keyboard.append([InlineKeyboardButton(suggestion, callback_data="noop")])

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(answer_text, reply_markup=reply_markup, parse_mode=None)

    except Exception as e:
        logger.error("Error handling text message: %s", e)
        await update.message.reply_text("מצטער, אירעה שגיאה. נסה שוב בעוד רגע.")


def create_bot_application() -> Application:
    """Create and configure the Telegram bot application."""
    global _bot_app

    if _bot_app is not None:
        return _bot_app

    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN must be set in environment variables")

    _bot_app = Application.builder().token(settings.telegram_bot_token).build()

    # Register handlers
    _bot_app.add_handler(CommandHandler("start", start_command))
    _bot_app.add_handler(CommandHandler("help", help_command))
    _bot_app.add_handler(CommandHandler("sections", sections_command))
    _bot_app.add_handler(CommandHandler("search", search_command))
    _bot_app.add_handler(CommandHandler("itinerary", itinerary_command))
    _bot_app.add_handler(CallbackQueryHandler(handle_callback_query))
    _bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    logger.info("Telegram bot application created")
    return _bot_app


async def setup_webhook(app: Application) -> None:
    """Register the webhook URL with Telegram API."""
    if not settings.webhook_url:
        logger.warning("WEBHOOK_URL not set, skipping webhook registration")
        return

    webhook_url = f"{settings.webhook_url}/telegram/webhook"
    try:
        await app.bot.set_webhook(url=webhook_url)
        logger.info("Telegram webhook set to: %s", webhook_url)
    except Exception as e:
        logger.error("Failed to set webhook: %s", e)
