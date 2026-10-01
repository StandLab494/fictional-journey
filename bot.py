import os
import sqlite3
import logging
import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8081").rstrip("/")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
PUBLISH_CHAT_ID = int(os.getenv("PUBLISH_CHAT_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "suggestions.db")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not ADMIN_CHAT_ID:
    raise RuntimeError("ADMIN_CHAT_ID is not set")
if not PUBLISH_CHAT_ID:
    raise RuntimeError("PUBLISH_CHAT_ID is not set")

apihelper.API_URL = f"{SERVER_URL}/bot{{0}}/{{1}}"
apihelper.FILE_URL = f"{SERVER_URL}/file/bot{{0}}/{{1}}"

bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS suggestions (
                moderation_message_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)

def save_suggestion(message_id, user_id):
    with db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO suggestions VALUES (?, ?, 'pending')",
            (message_id, user_id)
        )

def get_suggestion(message_id):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM suggestions WHERE moderation_message_id = ?",
            (message_id,)
        ).fetchone()

def set_status(message_id, status):
    with db() as conn:
        conn.execute(
            "UPDATE suggestions SET status = ? WHERE moderation_message_id = ?",
            (status, message_id)
        )

def moderation_keyboard():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ Опубликовать", callback_data="suggestion:approve"),
        InlineKeyboardButton("❌ Отклонить", callback_data="suggestion:reject"),
    )
    return kb

def done_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("ℹ️ Уже обработано", callback_data="suggestion:done"))
    return kb

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "Привет! 👋\n\n"
        "Это бот для предложений. Отправь сюда текст, фото, видео или файл.\n\n"
        "Сообщение попадёт на модерацию, а после одобрения будет опубликовано."
    )

@bot.message_handler(commands=["help"])
def help_handler(message):
    bot.send_message(
        message.chat.id,
        "Просто отправь своё предложение одним сообщением. "
        "Поддерживаются текст, фото, видео и файлы."
    )

SUPPORTED_TYPES = [
    "text", "photo", "video", "document", "audio",
    "voice", "animation", "sticker"
]

@bot.message_handler(
    content_types=SUPPORTED_TYPES,
    func=lambda m: m.chat.id != ADMIN_CHAT_ID
)
def suggestion_handler(message):
    try:
        copied = bot.copy_message(
            chat_id=ADMIN_CHAT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=moderation_keyboard(),
        )
        save_suggestion(copied.message_id, message.from_user.id)
        bot.reply_to(message, "✅ Предложение отправлено на модерацию. Спасибо!")
    except Exception:
        logger.exception("Failed to submit suggestion")
        bot.reply_to(message, "❌ Не удалось отправить предложение. Попробуй ещё раз.")

@bot.callback_query_handler(func=lambda call: call.data == "suggestion:approve")
def approve_handler(call):
    if call.message.chat.id != ADMIN_CHAT_ID:
        bot.answer_callback_query(call.id, "Нет доступа.", show_alert=True)
        return

    suggestion = get_suggestion(call.message.message_id)
    if not suggestion:
        bot.answer_callback_query(call.id, "Предложение не найдено.", show_alert=True)
        return
    if suggestion["status"] != "pending":
        bot.answer_callback_query(call.id, "Предложение уже обработано.")
        return

    try:
        bot.copy_message(
            chat_id=PUBLISH_CHAT_ID,
            from_chat_id=ADMIN_CHAT_ID,
            message_id=call.message.message_id,
        )
        set_status(call.message.message_id, "published")
        bot.edit_message_reply_markup(
            ADMIN_CHAT_ID, call.message.message_id, reply_markup=done_keyboard()
        )
        bot.answer_callback_query(call.id, "Опубликовано ✅")
        try:
            bot.send_message(suggestion["user_id"], "✅ Твоё предложение одобрено и опубликовано.")
        except Exception:
            logger.info("Could not notify user")
    except Exception:
        logger.exception("Failed to publish suggestion")
        bot.answer_callback_query(
            call.id,
            "Не удалось опубликовать. Проверь настройки канала.",
            show_alert=True,
        )

@bot.callback_query_handler(func=lambda call: call.data == "suggestion:reject")
def reject_handler(call):
    if call.message.chat.id != ADMIN_CHAT_ID:
        bot.answer_callback_query(call.id, "Нет доступа.", show_alert=True)
        return

    suggestion = get_suggestion(call.message.message_id)
    if not suggestion:
        bot.answer_callback_query(call.id, "Предложение не найдено.", show_alert=True)
        return
    if suggestion["status"] != "pending":
        bot.answer_callback_query(call.id, "Предложение уже обработано.")
        return

    set_status(call.message.message_id, "rejected")
    try:
        bot.edit_message_reply_markup(
            ADMIN_CHAT_ID, call.message.message_id, reply_markup=done_keyboard()
        )
    except Exception:
        logger.exception("Could not update moderation keyboard")

    bot.answer_callback_query(call.id, "Отклонено ❌")
    try:
        bot.send_message(suggestion["user_id"], "❌ Твоё предложение не прошло модерацию.")
    except Exception:
        logger.info("Could not notify user")

@bot.callback_query_handler(func=lambda call: call.data == "suggestion:done")
def done_handler(call):
    bot.answer_callback_query(call.id, "Предложение уже обработано.")

@bot.message_handler(
    func=lambda m: m.chat.id != ADMIN_CHAT_ID,
    content_types=["contact", "location", "venue", "poll", "dice", "video_note"]
)
def unsupported_handler(message):
    bot.reply_to(message, "Этот тип сообщения сейчас не поддерживается.")

if __name__ == "__main__":
    init_db()
    logger.info("Suggestion bot started")
    bot.infinity_polling(skip_pending=True)
