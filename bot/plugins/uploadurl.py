from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..services.user_service import is_verified
from ..services.telegram_login import get_client
from ..services.download_service import (
    download_from_url,
    download_from_telegram,
)
from ..helpers.validators import (
    is_telegram_url,
    parse_telegram_url,
)


@UtubeBot.on_message(filters.command("uploadurl"))
async def upload_url(_, m: Message):
    user_id = m.from_user.id

    if not is_verified(user_id):
        return await m.reply_text("❌ Verify first using /verify")

    if len(m.command) < 2:
        return await m.reply_text("❌ Usage: /uploadurl URL")

    url = m.command[1]

    await m.reply_text("🔍 Processing...")

    # Telegram URL
    if is_telegram_url(url):
        client = get_client(user_id)

        if not client:
            return await m.reply_text("❌ Login using /tglogin")

        try:
            chat_id, msg_id = parse_telegram_url(url)

            file_path = await download_from_telegram(
                client,
                chat_id,
                msg_id
            )

            await m.reply_text(f"✅ Downloaded:\n{file_path}")

        except Exception as e:
            await m.reply_text(f"❌ Error:\n{e}")

        return

    # Normal URL
    try:
        file_path = download_from_url(url)
        await m.reply_text(f"✅ Downloaded:\n{file_path}")

    except Exception as e:
        await m.reply_text(f"❌ Error:\n{e}")
