from ..services.fetch_service import fetch_video_from_link
from ..tg_session.session_manager import SessionManager

session = SessionManager()


async def smart_fetch(link: str):
    try:
        # Try normal method first
        return await fetch_video_from_link(link)

    except Exception as e:
        # fallback to user session
        started = await session.start()

        if not started:
            raise Exception("LOGIN_REQUIRED")

        try:
            parts = link.split("/")
            chat = parts[-2]
            msg_id = int(parts[-1])

            msg = await session.client.get_messages(chat, ids=msg_id)

            if not msg or not msg.media:
                raise Exception("No media")

            file_path = await msg.download_media(file="downloads/")
            return file_path

        except Exception as e:
            raise Exception(f"Fetch failed: {e}")
