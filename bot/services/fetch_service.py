import os
from telethon.errors import UsernameInvalidError, ChannelPrivateError

from ..userbot.client import userbot


async def fetch_video_from_link(link: str) -> str:
    if "t.me/" not in link:
        raise Exception("Invalid Telegram link")

    try:
        parts = link.split("/")
        chat = parts[-2]
        msg_id = int(parts[-1])

        async with userbot:
            msg = await userbot.get_messages(chat, ids=msg_id)

            if not msg:
                raise Exception("Message not found")

            if not msg.media:
                raise Exception("No media in message")

            os.makedirs("downloads", exist_ok=True)

            file_path = await msg.download_media(file="downloads/")

            return file_path

    except UsernameInvalidError:
        raise Exception("Invalid channel username")

    except ChannelPrivateError:
        raise Exception("Channel is private (join it with your account)")

    except Exception as e:
        raise Exception(f"Download failed: {e}")
