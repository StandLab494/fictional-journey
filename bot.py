import os

import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# =========================
# НАСТРОЙКИ
# =========================

SERVER_URL = "http://177.3.213.27:8081"

apihelper.API_URL = f"{SERVER_URL}/bot{{0}}/{{1}}"
apihelper.FILE_URL = f"{SERVER_URL}/file/bot{{0}}/{{1}}"


# =========================
# ТОКЕН ИЗ RAILWAY
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "Переменная окружения BOT_TOKEN не найдена в Railway."
    )


# =========================
# СОЗДАНИЕ БОТА
# =========================

bot = telebot.TeleBot(TOKEN)


# =========================
# ГЛАВНОЕ МЕНЮ HELP
# =========================

def help_menu():
    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton(
            "👮🏻 Базовые команды",
            callback_data="help_base"
        ),
        InlineKeyboardButton(
            "⚠️ Предупреждения",
            callback_data="help_warns"
        ),
        InlineKeyboardButton(
            "🛠 Управление сообщениями",
            callback_data="help_messages"
        ),
        InlineKeyboardButton(
            "📌 Закрепленные сообщения",
            callback_data="help_pinned"
        ),
        InlineKeyboardButton(
            "👥 Управление участниками",
            callback_data="help_members"
        ),
        InlineKeyboardButton(
            "📊 Статистика и информация",
            callback_data="help_stats"
        ),
        InlineKeyboardButton(
            "🧠 Команды для экспертов",
            callback_data="help_expert"
        )
    )

    return markup


# =========================
# /START
# =========================

@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "👋 Привет!\n"
        "Group Help наиболее полный бот, который поможет вам легко "
        "и безопасно управлять вашими группами!\n\n"
        "👉 Добавьте меня в супергруппу и сделайте меня Администратором, "
        "чтобы я сразу же начал действовать!\n\n"
        "❓ КАКИЕ КОМАНДЫ?\n"
        "Нажмите /help, чтобы увидеть все команды и то, как они работают!"
    )

    bot.send_message(
        message.chat.id,
        text
    )


# =========================
# /HELP
# =========================

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "❓ <b>Group Help — список команд</b>\n\n"
        "Выберите нужный раздел:",
        parse_mode="HTML",
        reply_markup=help_menu()
    )


# =========================
# ТЕКСТЫ РАЗДЕЛОВ HELP
# =========================

HELP_SECTIONS = {

    "help_base": (
        "👮🏻 <b>Базовые команды</b>\n\n"

        "👮🏻 <b>/reload</b>\n"
        "Обновляет список администраторов и их привилегии.\n\n"

        "🕵🏻 <b>/settings</b>\n"
        "Управление всеми настройками бота в группе.\n\n"

        "👮🏻 <b>/ban</b>\n"
        "Заблокировать пользователя в группе. "
        "Пользователь не сможет вернуться по ссылке группы.\n\n"

        "👮🏻 <b>/mute</b>\n"
        "Ограничить пользователю возможность писать сообщения.\n\n"

        "👮🏻 <b>/kick</b>\n"
        "Удалить пользователя из группы. "
        "После этого он сможет снова зайти по ссылке.\n\n"

        "👮🏻 <b>/unban</b>\n"
        "Убрать пользователя из чёрного списка.\n\n"

        "👮🏻 <b>/info</b>\n"
        "Информация о пользователе.\n\n"

        "👮🏻 <b>/infopvt</b>\n"
        "Информация о пользователе в личных сообщениях.\n\n"

        "◽️ <b>/staff</b>\n"
        "Полный список администрации группы."
    ),

    "help_warns": (
        "⚠️ <b>Предупреждения</b>\n\n"

        "👮🏻 <b>/warn</b>\n"
        "Выдать пользователю предупреждение.\n\n"

        "👮🏻 <b>/unwarn</b>\n"
        "Снять предупреждение с пользователя.\n\n"

        "👮🏻 <b>/warns</b>\n"
        "Показать предупреждения пользователя.\n\n"

        "🕵🏻 <b>/delwarn</b>\n"
        "Удалить сообщение и выданное за него предупреждение."
    ),

    "help_messages": (
        "🛠 <b>Управление сообщениями</b>\n\n"

        "🛃 <b>/del</b>\n"
        "Удалить выбранное сообщение.\n\n"

        "🛃 <b>/logdel</b>\n"
        "Удалить сообщение и отправить информацию о событии "
        "в канал событий, если он настроен.\n\n"

        "◽️ <b>/me</b>\n"
        "Отправить личное сообщение с информацией о пользователе "
        "и группе, предупреждениями, правилами, запрещёнными словами "
        "и другими данными.\n\n"

        "🕵🏻 <b>/send</b>\n"
        "Опубликовать HTML-сообщение от имени бота в группе.\n\n"
        "Пример: <code>/send Привет, мир!</code>\n\n"

        "👮🏻 <b>/intervention</b>\n"
        "Запросить вмешательство официальной поддержки бота."
    ),

    "help_pinned": (
        "📌 <b>Закрепленные сообщения</b>\n\n"

        "🕵🏻 <b>/pin [сообщение]</b>\n"
        "Отправить сообщение через бота и закрепить его.\n\n"

        "🕵🏻 <b>/pin</b>\n"
        "В ответ на сообщение закрепить его.\n\n"

        "🕵🏻 <b>/editpin [сообщение]</b>\n"
        "Изменить текущее закреплённое сообщение, "
        "если оно было отправлено ботом.\n\n"

        "🕵🏻 <b>/delpin</b>\n"
        "Удалить закреплённое сообщение.\n\n"

        "🕵🏻 <b>/repin</b>\n"
        "Удалить и заново закрепить сообщение с уведомлением.\n\n"

        "👥 <b>/pinned</b>\n"
        "Найти последнее закреплённое сообщение."
    ),

    "help_members": (
        "👥 <b>Управление участниками</b>\n\n"

        "🕵🏻 <b>/inactives [дней]</b>\n"
        "Отправить в личные сообщения список неактивных пользователей "
        "с возможностью их заблокировать или удалить.\n\n"

        "🕵🏻 <b>/list</b>\n"
        "Отправить в личные сообщения список пользователей "
        "с количеством их сообщений.\n\n"

        "🕵🏻 <b>/list roles</b>\n"
        "Показать список пользователей со специальными ролями."
    ),

    "help_stats": (
        "📊 <b>Статистика и информация</b>\n\n"

        "👥 <b>/geturl</b>\n"
        "В ответ на сообщение отправляет прямую ссылку на него.\n\n"

        "🕵🏻 <b>/list</b>\n"
        "Список пользователей и количество их сообщений.\n\n"

        "🕵🏻 <b>/list roles</b>\n"
        "Список пользователей со специальными ролями.\n\n"

        "🕵🏻 <b>/graphic</b>\n"
        "График динамики вступления участников.\n\n"

        "🕵🏻 <b>/trend</b>\n"
        "Статистика роста группы."
    ),

    "help_expert": (
        "🧠 <b>Команды для экспертов</b>\n\n"

        "👥 <b>/geturl</b>\n"
        "При ответе на сообщение отправляет прямую ссылку на него.\n\n"

        "🕵🏻 <b>/inactives [дней]</b>\n"
        "Показывает список неактивных пользователей "
        "с возможностью управления ими.\n\n"

        "🕵🏻 <b>/graphic</b>\n"
        "Показывает график динамики участников.\n\n"

        "🕵🏻 <b>/trend</b>\n"
        "Показывает статистику роста группы."
    )
}


# =========================
# CALLBACK КНОПОК HELP
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("help_")
    and call.data != "help_back"
)
def help_callback(call):
    text = HELP_SECTIONS.get(call.data)

    if not text:
        bot.answer_callback_query(
            call.id,
            "Раздел не найден."
        )
        return

    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="help_back"
        )
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=markup
    )


# =========================
# НАЗАД В HELP
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "help_back"
)
def help_back(call):
    bot.answer_callback_query(call.id)

    bot.edit_message_text(
        "❓ <b>Group Help — список команд</b>\n\n"
        "Выберите нужный раздел:",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
        reply_markup=help_menu()
    )


# =========================
# ЗАПУСК БОТА
# =========================

if __name__ == "__main__":
    print("Group Help запущен.")

    bot.infinity_polling(
        skip_pending=True
  )
