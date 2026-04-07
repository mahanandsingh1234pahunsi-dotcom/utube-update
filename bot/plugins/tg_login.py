# bot/plugins/tg_login.py

from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..tg_session.session_manager import SessionManager


session = SessionManager()

# Temporary in-memory storage (for OTP flow)
user_states = {}


# ================= LOGIN =================

@UtubeBot.on_message(filters.command("tg_login"))
async def tg_login(c, m: Message):

    if len(m.command) < 2:
        await m.reply(
            "❌ Usage:\n"
            "/tg_login PHONE_NUMBER\n\n"
            "Example:\n/tg_login +911234567890"
        )
        return

    phone = m.command[1]

    try:
        await session.login(phone)

        user_states[m.from_user.id] = phone

        await m.reply(
            "📩 OTP sent successfully!\n\n"
            "Now send:\n"
            "/tg_otp YOUR_CODE"
        )

    except Exception as e:
        await m.reply(f"❌ Failed to send OTP:\n{e}")


# ================= VERIFY OTP =================

@UtubeBot.on_message(filters.command("tg_otp"))
async def tg_otp(c, m: Message):

    if len(m.command) < 2:
        await m.reply(
            "❌ Usage:\n"
            "/tg_otp CODE"
        )
        return

    code = m.command[1]
    user_id = m.from_user.id

    if user_id not in user_states:
        await m.reply("❌ Please start login first using /tg_login")
        return

    try:
        await session.verify(code)

        user_states.pop(user_id, None)

        await m.reply(
            "✅ Telegram account linked successfully!\n\n"
            "Now retry your /upload command 🚀"
        )

    except Exception as e:
        await m.reply(f"❌ Verification failed:\n{e}")


# ================= LOGOUT =================

@UtubeBot.on_message(filters.command("tg_logout"))
async def tg_logout(c, m: Message):

    try:
        await session.logout()

        await m.reply("✅ Logged out successfully!")

    except Exception as e:
        await m.reply(f"❌ Logout failed:\n{e}")
