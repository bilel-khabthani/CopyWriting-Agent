"""Phase 2: Telegram bot UI with a format selector.

Flow: /start -> pick a category -> pick a format -> answer a short guided form
(common questions + a few format-specific ones) -> generate -> export PDF.

The heavy, format-aware work lives in :mod:`pipeline` (``run_for_format``) and
:mod:`prompts_formats`. This module only drives the conversation.
"""

import asyncio
import logging
import os
import subprocess
import threading
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import config
import exporter
import formats
from formats import FORMAT_VIDEO_AD
from pipeline import PipelineError, run_for_format
from renderer import format_internal, markdown_to_plain, split_message

logger = logging.getLogger(__name__)

CATEGORY, FORMAT, ASK, CONFIRM = range(4)

_NONE_ANSWERS = {"-", "n/a", "none", "aucun"}

INTRO = (
    "Welcome to AdScript Studio.\n\n"
    "I turn a short brief into ready-to-use marketing copy: video ads, "
    "landing pages, product sheets, online ads, emails, social posts, "
    "podcasts, flyers, posters and sales letters.\n\n"
    "Send /cancel at any time to stop."
)

GOAL_OPTIONS = [
    ("Sell the product", "sell the product"),
    ("Get leads", "get leads"),
    ("Brand awareness", "brand awareness"),
]

PLATFORM_OPTIONS = [
    ("TikTok", "TikTok"),
    ("Instagram Reels", "Instagram Reels"),
    ("YouTube Shorts", "YouTube Shorts"),
    ("YouTube", "YouTube"),
]

PRODUCT_TYPE_OPTIONS = [
    ("Physical product", "physical product"),
    ("App / software", "app or software"),
    ("Service", "service"),
]

TONE_OPTIONS = [
    ("Warm & friendly", "warm and friendly"),
    ("Bold & energetic", "bold and energetic"),
    ("Professional", "professional"),
    ("Playful & fun", "playful and fun"),
]


# --------------------------------------------------------------------------- #
# Guided form: build the ordered list of questions for a chosen format
# --------------------------------------------------------------------------- #

def build_steps(format_key: str) -> list:
    """Ordered list of steps for a format: common questions + format extras."""
    steps = [
        {
            "field": "brand",
            "label": "Brand",
            "type": "text",
            "prompt": "What is the brand or product name? (e.g. AquaSmart). "
            "If it has no name, send a dash -",
        },
        {
            "field": "product",
            "label": "Product",
            "type": "text",
            "prompt": "Describe the product or service in a few sentences.",
        },
        {
            "field": "details",
            "label": "Features",
            "type": "text",
            "prompt": "What are the top 2-3 features or benefits? "
            "(materials, what makes it unique, price). A short line is fine.",
        },
        {
            "field": "audience",
            "label": "Audience",
            "type": "text",
            "prompt": "Who is the target audience? (e.g. busy parents aged 28-45)",
        },
        {
            "field": "goal",
            "label": "Goal",
            "type": "select",
            "prompt": "What is the main goal?",
            "options": GOAL_OPTIONS,
        },
    ]

    if format_key == FORMAT_VIDEO_AD:
        steps += [
            {
                "field": "platform",
                "label": "Platform",
                "type": "select",
                "prompt": "Which platform is this for?",
                "options": PLATFORM_OPTIONS,
            },
            {
                "field": "product_type",
                "label": "Type",
                "type": "select",
                "prompt": "What type of product is this?",
                "options": PRODUCT_TYPE_OPTIONS,
            },
        ]

    for field, question in formats.extra_fields_for(format_key):
        steps.append(
            {
                "field": field,
                "label": field.replace("_", " ").title(),
                "type": "text",
                "prompt": question,
            }
        )

    steps.append(
        {
            "field": "tone",
            "label": "Tone",
            "type": "select",
            "prompt": "What tone should it have?",
            "options": TONE_OPTIONS,
        }
    )
    return steps


# --------------------------------------------------------------------------- #
# Keyboards
# --------------------------------------------------------------------------- #

def _option_keyboard(options) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(label, callback_data="opt:{0}".format(i))]
        for i, (label, _value) in enumerate(options)
    ]
    return InlineKeyboardMarkup(rows)


def _category_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(name, callback_data="cat:{0}".format(key))]
        for key, name in formats.CATEGORIES
    ]
    return InlineKeyboardMarkup(rows)


def _format_keyboard(category: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(name, callback_data="fmt:{0}".format(key))]
        for key, name in formats.formats_in_category(category)
    ]
    rows.append([InlineKeyboardButton("<< Back", callback_data="cat:")])
    return InlineKeyboardMarkup(rows)


def restricted(func):
    """Allow only configured Telegram user IDs (empty allowlist = everyone)."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if config.ALLOWED_USER_IDS and (user is None or user.id not in config.ALLOWED_USER_IDS):
            if update.callback_query:
                await update.callback_query.answer("This bot is private.", show_alert=True)
            elif update.message:
                await update.message.reply_text("Sorry, this bot is private.")
            return ConversationHandler.END
        return await func(update, context, *args, **kwargs)

    return wrapper


# --------------------------------------------------------------------------- #
# Conversation handlers
# --------------------------------------------------------------------------- #

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(INTRO)
    await update.message.reply_text(
        "What kind of copy do you need?", reply_markup=_category_keyboard()
    )
    return CATEGORY


@restricted
async def category_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data.split(":", 1)[1]
    if not category:
        await query.edit_message_text(
            "What kind of copy do you need?", reply_markup=_category_keyboard()
        )
        return CATEGORY
    context.user_data["category"] = category
    await query.edit_message_text(
        "{0} - choose a format:".format(formats.category_name(category)),
        reply_markup=_format_keyboard(category),
    )
    return FORMAT


@restricted
async def format_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    key = query.data.split(":", 1)[1]
    meta = formats.get_format(key)
    if meta is None:
        await query.edit_message_text("Unknown format. Send /start to try again.")
        return ConversationHandler.END

    context.user_data["format"] = key
    context.user_data["steps"] = build_steps(key)
    context.user_data["_idx"] = 0
    await query.edit_message_text("Format: {0}".format(meta["name"]))
    await _ask(context, query.message.chat_id)
    return ASK


async def _ask(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Send the question for the current step (no-op if the steps are done)."""
    steps = context.user_data.get("steps") or []
    idx = context.user_data.get("_idx", 0)
    if idx >= len(steps):
        return
    step = steps[idx]
    if step["type"] == "select":
        await context.bot.send_message(
            chat_id, step["prompt"], reply_markup=_option_keyboard(step["options"])
        )
    else:
        await context.bot.send_message(chat_id, step["prompt"])


async def _advance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Move to the next question, or the confirmation screen when finished."""
    chat_id = update.effective_chat.id
    steps = context.user_data.get("steps") or []
    if context.user_data.get("_idx", 0) >= len(steps):
        await _show_confirm(context, chat_id)
        return CONFIRM
    await _ask(context, chat_id)
    return ASK


@restricted
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    steps = context.user_data.get("steps") or []
    idx = context.user_data.get("_idx", 0)
    if idx >= len(steps):
        return ConversationHandler.END
    step = steps[idx]
    if step["type"] != "text":
        await update.message.reply_text("Please use the buttons above.")
        return ASK

    value = update.message.text.strip()
    if step["field"] == "brand" and value.lower() in _NONE_ANSWERS:
        value = ""
    context.user_data[step["field"]] = value
    context.user_data["_idx"] = idx + 1
    return await _advance(update, context)


@restricted
async def on_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    steps = context.user_data.get("steps") or []
    idx = context.user_data.get("_idx", 0)
    if idx >= len(steps):
        return ConversationHandler.END
    step = steps[idx]
    if step["type"] != "select":
        return ASK
    try:
        choice = int(query.data.split(":", 1)[1])
        value = step["options"][choice][1]
    except (ValueError, IndexError):
        return ASK
    context.user_data[step["field"]] = value
    context.user_data["_idx"] = idx + 1
    return await _advance(update, context)


def _summary(context: ContextTypes.DEFAULT_TYPE) -> str:
    meta = formats.get_format(context.user_data.get("format", FORMAT_VIDEO_AD))
    lines = ["Here is your brief:", ""]
    if meta:
        lines.append("Format: {0}".format(meta["name"]))
    for step in context.user_data.get("steps", []):
        value = context.user_data.get(step["field"], "")
        if value:
            lines.append("{0}: {1}".format(step["label"], value))
    lines += ["", "Tap Generate to create it."]
    return "\n".join(lines)


async def _show_confirm(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Generate", callback_data="generate")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")],
        ]
    )
    await context.bot.send_message(chat_id, _summary(context), reply_markup=keyboard)


async def _send(bot, chat_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id, text, parse_mode=ParseMode.MARKDOWN)
    except BadRequest:
        await bot.send_message(chat_id, markdown_to_plain(text))


async def _generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    status_id = query.message.message_id
    loop = asyncio.get_running_loop()

    format_key = context.user_data.get("format", FORMAT_VIDEO_AD)
    brief = {}
    for step in context.user_data.get("steps", []):
        brief[step["field"]] = context.user_data.get(step["field"], "")

    async def edit_status(text: str) -> None:
        try:
            await context.bot.edit_message_text(
                text, chat_id=chat_id, message_id=status_id
            )
        except BadRequest:
            pass

    def on_progress(message: str) -> None:
        try:
            asyncio.run_coroutine_threadsafe(edit_status(message), loop).result(timeout=30)
        except Exception:
            pass

    await context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    try:
        result = await asyncio.to_thread(run_for_format, format_key, brief, on_progress)
    except PipelineError as exc:
        await edit_status("Could not generate it.\n\n{0}".format(exc))
        return ConversationHandler.END
    except Exception as exc:
        logger.exception("Pipeline crashed")
        await edit_status("Unexpected error: {0}".format(exc))
        return ConversationHandler.END

    try:
        await context.bot.delete_message(chat_id, status_id)
    except Exception:
        pass

    context.user_data["last_result"] = result

    for chunk in split_message(format_internal(result)):
        await _send(context.bot, chat_id, chunk)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Client PDF", callback_data="export:client"),
                InlineKeyboardButton("Full report PDF", callback_data="export:full"),
            ],
            [InlineKeyboardButton("New brief", callback_data="newbrief")],
        ]
    )
    await context.bot.send_message(
        chat_id, "Export this as a PDF, or start a new brief:", reply_markup=keyboard
    )
    return ConversationHandler.END


@restricted
async def export_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    result = context.user_data.get("last_result")
    if result is None:
        await context.bot.send_message(chat_id, "Please generate something first (/start).")
        return

    client_view = query.data == "export:client"
    try:
        path, filename = exporter.build_pdf_file(result, client_view=client_view)
    except Exception:
        logger.exception("PDF export failed")
        await context.bot.send_message(chat_id, "Sorry, I could not build the PDF.")
        return

    try:
        await context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        with open(path, "rb") as handle:
            await context.bot.send_document(
                chat_id, document=handle, filename=filename
            )
    except Exception:
        logger.exception("Sending PDF failed")
        await context.bot.send_message(chat_id, "Sorry, I could not send the PDF.")


@restricted
async def new_brief_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """'New brief' entry point: clear state and restart the format selector."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text(
        "What kind of copy do you need?", reply_markup=_category_keyboard()
    )
    return CATEGORY


@restricted
async def confirm_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "Cancelled. Send /start to begin again."
        )
        return ConversationHandler.END
    return await _generate(update, context)


@restricted
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled. Send /start to begin again.")
    return ConversationHandler.END


@restricted
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Send /start to pick a format and build a brief.\n"
        "/cancel to stop the current form.\n"
        "/id to show your Telegram ID."
    )


@restricted
async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Your Telegram ID: {0}\n\n"
        "Add it to ALLOWED_USER_IDS in .env to lock the bot to you.".format(
            update.effective_user.id
        )
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Update %s caused error %s", update, context.error)


def _setup_logging() -> None:
    handlers = [logging.StreamHandler()]
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.LOG_FILE)
    try:
        handlers.append(
            RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        )
    except OSError as exc:
        print("Could not open log file {0}: {1}".format(log_path, exc))
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
        handlers=handlers,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def _start_ollama() -> None:
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        logger.info("Launching 'ollama serve'...")
    except FileNotFoundError:
        logger.error("'ollama' executable not found on PATH.")


def _ensure_ollama() -> bool:
    from ollama_client import OllamaClient

    client = OllamaClient()
    try:
        if not client.is_available():
            logger.warning("Ollama not reachable at %s; trying to start it.", config.OLLAMA_HOST)
            _start_ollama()
            for _ in range(10):
                time.sleep(1.5)
                if client.is_available():
                    break
        if not client.is_available():
            logger.error("Ollama is still unreachable. Start it with: ollama serve")
            return False
        if not client.model_installed():
            logger.warning(
                "Model '%s' is not installed. Run: ollama pull %s", config.MODEL, config.MODEL
            )
        logger.info("Ollama health check passed.")
        return True
    finally:
        client.close()


def _warmup() -> None:
    from ollama_client import OllamaClient

    try:
        client = OllamaClient()
        try:
            client.chat(
                [{"role": "user", "content": "ping"}], temperature=0.0, num_predict=1
            )
            logger.info("Model warmup complete (%s).", config.MODEL)
        finally:
            client.close()
    except Exception as exc:
        logger.warning("Model warmup failed: %s", exc)


def main() -> None:
    _setup_logging()
    if not config.BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is missing. Add it to .env")

    _ensure_ollama()
    threading.Thread(target=_warmup, daemon=True).start()

    application = Application.builder().token(config.BOT_TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CommandHandler(["start", "script"], start),
            CallbackQueryHandler(new_brief_cb, pattern=r"^newbrief$"),
        ],
        states={
            CATEGORY: [CallbackQueryHandler(category_cb, pattern=r"^cat:")],
            FORMAT: [
                CallbackQueryHandler(format_cb, pattern=r"^fmt:"),
                CallbackQueryHandler(category_cb, pattern=r"^cat:"),
            ],
            ASK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_text),
                CallbackQueryHandler(on_select, pattern=r"^opt:"),
            ],
            CONFIRM: [CallbackQueryHandler(confirm_cb, pattern=r"^(generate|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conversation)
    application.add_handler(CallbackQueryHandler(export_cb, pattern=r"^export:"))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("id", id_cmd))
    application.add_error_handler(on_error)

    logger.info("AdScript bot is running. Models: %s (fallback %s)", config.MODEL, config.FALLBACK_MODEL)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
