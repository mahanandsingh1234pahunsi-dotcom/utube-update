from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..services.telegram_login import create_client


@UtubeBot.on_message(filters.command("tglogin"))
async def tg_login(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ Usage: /tglogin PHONE")

    phone = m.command[1]

    client = create_client(m.from_user.id)
    await client.connect()

    try:
        sent = await client.send_code(phone)

        # store phone_code_hash temporarily
        client.phone_code_hash = sent.phone_code_hash
        client.phone = phone

        await m.reply_text(
            "📲 OTP sent!\nUse:\n/tgotp YOUR_CODE"
        )

    except Exception as e:
        await m.reply_text(f"❌ Error:\n{e}")
