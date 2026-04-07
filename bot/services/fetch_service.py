# bot/services/smart_fetch.py

import re
import os

from ..services.fetch_service import fetch_video_from_link
from ..tg_session.session_manager import SessionManager

session = SessionManager()


# ================= LINK PARSER =================

def parse_link(link: str):
    """
    Supports:
    https://t.me/channel/123
    https://t.me/c/123456789/456
    https://t.me/+invite/xxx (not supported)
    """

    if "t.me/c/" in link:
        # Private supergroup/channel
        match = re.search(r"t\.me/c/(\d+)/(\d+)", link)
        if not match:
            raise Exception("Invalid private link")

        chat_id = int("-100" + match.group(1))
        msg_id = int(match.group(2))
        return chat_id, msg_id

    else:
        # Public channel
        match = re.search(r"t\.me/([^/]+)/(\d+)", link)
        if not match:
            raise Exception("Invalid link")

        chat = match.group(1)
        msg_id = int(match.group(2))
        return chat, msg_id


# ================= SMART FETCH =================

async def smart_fetch(link: str):

    # STEP 1: Try normal bot fetch
    try:
        return await fetch_video_from_link(link)

    except Exception:
        pass  # fallback

    # STEP 2: Use user session
    started = await session.start()

    if not started:
        raise Exception("LOGIN_REQUIRED")

    try:
        chat, msg_id = parse_link(link)

        msg = await session.client.get_messages(chat, ids=msg_id)

        if not msg:
            raise Exception("Message not found")

        if not msg.media:
            raise Exception("No media")

        # Ensure downloads folder exists
        os.makedirs("downloads", exist_ok=True)

        file_path = await msg.download_media(file="downloads/")
        return file_path

    except Exception as e:
        err = str(e)

        if "Message not found" in err:
            raise Exception("Message not accessible")

        raise Exception(f"Fetch failed: {err}")
