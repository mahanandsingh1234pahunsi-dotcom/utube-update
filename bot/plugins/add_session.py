# bot/plugins/add_session.py

from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..tg_session.session_manager import SessionManager

session = SessionManager()


@UtubeBot.on_message(filters.command("add_session") & filters.private)
async def add_session_handler(client, message: Message):

    user_id = message.from_user.id

    # Check if session string provided
    if len(message.command) < 2:
        await message.reply_text(
            "❌ Please provide session string.\n\n"
            "Usage:\n"
            "/add_session YOUR_SESSION_STRING"
        )
        return

    # Extract full session string safely
    session_str = message.text.split(" ", 1)[1].strip()

    # Basic validation (important)
    if len(session_str) < 20:
        await message.reply_text("❌ Invalid session string.")
        return

    try:
        # Save session
        await session.save(user_id, session_str)

        # Try to start session (verify it works)
        client_session = await session.start(user_id)

        if not client_session:
            raise Exception("Invalid session")

        await message.reply_text(
            "✅ Session added & verified successfully!\n\n"
            "🚀 Now you can upload from private channels."
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Failed to add session:\n{e}"
  )
