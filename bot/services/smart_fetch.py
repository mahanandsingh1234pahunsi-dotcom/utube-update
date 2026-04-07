# bot/services/smart_fetch.py

from ..services.fetch_service import fetch_video_from_link
from ..tg_session.session_manager import SessionManager

session = SessionManager()


async def smart_fetch(link: str, user_id: int):

    # ================= PUBLIC FETCH =================
    try:
        return await fetch_video_from_link(link)
    except:
        pass

    # ================= PRIVATE FETCH =================
    client = await session.start(user_id)

    if not client:
        raise Exception("LOGIN_REQUIRED")

    try:
        parts = link.strip("/").split("/")
        chat = parts[-2]
        msg_id = int(parts[-1])

        msg = await client.get_messages(chat, ids=msg_id)

        if not msg or not msg.media:
            raise Exception("No media found")

        file_path = await msg.download_media(file="downloads/")
        return file_path

    except Exception as e:
        raise Exception(f"Fetch failed: {e}")
