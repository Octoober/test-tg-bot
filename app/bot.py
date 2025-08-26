from email import message
import os
import time
import uuid
import aiosqlite
from pathlib import Path
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN") or None
ADMIN_ID = os.environ.get("ADMIN_ID") or None
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or None
PORT = int(os.environ.get("PORT", 8080))
ROOT_PATH = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_PATH / "data" / "bot.db"


async def init_database() -> None:
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL, 
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                
            )
            """
        )
        await conn.commit()


async def add_user(update: Update, context: ContextTypes) -> None:
    user = update.effective_user
    user_id = user.id
    username = user.username
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            await conn.execute(
                "INSERT INTO user (user_id, username) VALUES (?,?)", (user_id, username)
            )
            await conn.commit()
    except aiosqlite.IntegrityError:
        await update.message.reply_text("юзер уже в бд")
        return

    await update.message.reply_text(f"добавил {username} в бд")


async def show_users(update: Update, context: ContextTypes) -> None:
    user = update.effective_user
    user_id = user.id
    username = user.username
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT user_id, username FROM user")
        users = await cursor.fetchall()

    if not users:
        await update.message.reply_text("Нет юзеров в бд")
        return

    user_list = [f"@{user[1]} (ID: {user[0]})" for user in users]
    message = "Юзеры в бд:\n" + "\n".join(user_list)

    await update.message.reply_text(message)


async def post_init(application: Application) -> None:
    print("POST_INIT")
    msg = "init"
    if not ADMIN_ID:
        print("ADMIN_ID is None")
        return
    await application.bot.sendMessage(ADMIN_ID, msg)
    await init_database()


def init_bot() -> None:
    if BOT_TOKEN == None:
        print("BOT TOKEN is None")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("users", show_users))

    if WEBHOOK_URL:
        print("Run webhook")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            url_path="/telegram",
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        print("Run polling")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    print(f"hi v2 ({time.time()}) - {uuid.uuid4()}")
    print(f"BOT: {BOT_TOKEN}")
    print(f"DB PATH: {DB_PATH}")

    init_bot()


if __name__ == "__main__":
    main()
