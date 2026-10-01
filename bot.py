import os
import sqlite3
import logging

import telebot
from telebot import apihelper

TOKEN = os.getenv("BOT_TOKEN")
SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8081").rstrip("/")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "messages.db")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not ADMIN_USER_ID:
    raise RuntimeError("ADMIN_USER_ID is not set")

apihelper.API_URL = f"{SERVER_URL}/bot{{0}}/{{1}}"
apihelper.FILE_URL = f"{SERVER_URL}/file/bot{{0}}/{{1}}"

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                admin_message_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL
            )
        """)


def save_message(admin_message_id, user_id):
    with db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO messages (admin_message_id, user_id) VALUES (?, ?)",
            (admin_message_id, user_id),
        )


def get_user_id(admin_message_id):
    with db() as conn:
        row = conn.execute(
            "SELECT user_id FROM messages WHERE admin_message_id = ?",
            (admin_message_id,),
        ).fetchone()
        return row["user_id"] if row else None


@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        "Привет! 👋\n\n"
        "Напиши сюда сообщение, и я передам его администратору. "
        "Администратор сможет ответить тебе прямо через бота.",
    )


@bot.message_handler(commands=["help"])
def help_handler(message):
    bot.send_message(
        message.chat.id,
        "Просто отправь сообщение сюда. "
        "Я передам его администратору, а его ответ придёт тебе в этот чат.",
    )


SUPPORTED_TYPES = [
    "text",
    "photo",
    "video",
    "document",
    "audio",
    "voice",
    "animation",
    "sticker",
    "video_note",
]


@bot.message_handler(
    content_types=SUPPORTED_TYPES,
    func=lambda m: m.from_user.id != ADMIN_USER_ID,
)
def user_message_handler(message):
    try:
        copied = bot.copy_message(
            chat_id=ADMIN_USER_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        save_message(copied.message_id, message.from_user.id)
        bot.reply_to(message, "✅ Сообщение отправлено.")
    except Exception:
        logger.exception("Failed to forward user message")
        bot.reply_to(message, "❌ Не удалось отправить сообщение. Попробуй ещё раз.")


@bot.message_handler(
    content_types=SUPPORTED_TYPES,
    func=lambda m: (
        m.from_user.id == ADMIN_USER_ID
        and m.reply_to_message is not None
    ),
)
def admin_reply_handler(message):
    user_id = get_user_id(message.reply_to_message.message_id)
    if not user_id:
        return

    try:
        bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        bot.reply_to(message, "✅ Ответ отправлен.")
    except Exception:
        logger.exception("Failed to send admin reply")
        bot.reply_to(message, "❌ Не удалось отправить ответ.")


@bot.message_handler(
    func=lambda m: m.from_user.id != ADMIN_USER_ID,
    content_types=[
        "contact",
        "location",
        "venue",
        "poll",
        "dice",
    ],
)
def unsupported_handler(message):
    bot.reply_to(message, "Этот тип сообщения сейчас не поддерживается.")


if __name__ == "__main__":
    init_db()
    logger.info("Support bot started")
    bot.infinity_polling(skip_pending=True)
