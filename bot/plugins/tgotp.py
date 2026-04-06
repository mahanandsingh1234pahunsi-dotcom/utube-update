from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..services.telegram_login import get_client


@UtubeBot.on_message(filters.command("tgotp"))
async def tg_otp(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ Usage: /tgotp OTP")

    otp = m.command[1]

    client = get_client(m.from_user.id)

    if not client:
        return await m.reply_text("❌ Use /tglogin first")

    try:
        await client.sign_in(
            phone_number=client.phone,
            phone_code=otp,
            phone_code_hash=client.phone_code_hash
        )

        await m.reply_text("✅ Telegram login successful!")

    except Exception as e:
        await m.reply_text(f"❌ Failed:\n{e}")
