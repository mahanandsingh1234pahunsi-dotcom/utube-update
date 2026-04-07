import os
from telethon.tl.types import MessageMediaDocument

from ..userbot.client import userbot


async def fetch_video_from_link(link: str) -> str:
    """
    Downloads video from Telegram private/public link
    Returns file path
    """

    if "t.me/" not in link:
        raise Exception("Invalid Telegram link")

    parts = link.split("/")
    chat = parts[-2]
    msg_id = int(parts[-1])

    async with userbot:
        msg = await userbot.get_messages(chat, ids=msg_id)

        if not msg or not msg.media:
            raise Exception("No media found")

        file_path = await msg.download_media(file="downloads/")

        return file_path
