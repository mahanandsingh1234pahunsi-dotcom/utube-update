# bot/services/fetch_service.py

import os
import yt_dlp


async def fetch_video_from_link(link: str):
    """
    Download video from public Telegram / direct / other links
    """

    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "format": "best",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)

        return file_path

    except Exception as e:
        raise Exception(f"Public fetch failed: {e}")
