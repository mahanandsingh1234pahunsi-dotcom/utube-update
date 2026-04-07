from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..tg_session.session_manager import SessionManager

session = SessionManager()


@UtubeBot.on_message(filters.command("tg_login"))
async def tg_login(c, m: Message):
    phone = m.command[1]

    await session.login(phone)

    await m.reply("📩 OTP sent!\nSend:\n/tg_otp CODE")


@UtubeBot.on_message(filters.command("tg_otp"))
async def tg_otp(c, m: Message):
    code = m.command[1]
    phone = "your_phone_here"  # store temporarily if needed

    await session.verify(phone, code)

    await m.reply("✅ Telegram login successful!")
