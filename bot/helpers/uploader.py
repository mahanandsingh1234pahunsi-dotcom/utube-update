import os
import random
import asyncio
import logging
from typing import Optional, Tuple, Callable

from ..youtube import GoogleAuth, YouTube
from ..config import Config


log = logging.getLogger(__name__)


class Uploader:
    def __init__(self, file: str, title: Optional[str] = None):
        self.file = file
        self.title = title

        self.video_category = {
            1: "Film & Animation",
            2: "Autos & Vehicles",
            10: "Music",
            15: "Pets & Animal",
            17: "Sports",
            19: "Travel & Events",
            20: "Gaming",
            22: "People & Blogs",
            23: "Comedy",
            24: "Entertainment",
            25: "News & Politics",
            26: "Howto & Style",
            27: "Education",
            28: "Science & Technology",
            29: "Nonprofits & Activism",
        }

    async def start(self, progress: Callable = None, *args) -> Tuple[bool, str]:
        self.progress = progress
        self.args = args

        await self._upload()

        return self.status, self.message

    async def _upload(self) -> None:
        try:
            loop = asyncio.get_running_loop()

            auth = GoogleAuth(Config.CLIENT_ID, Config.CLIENT_SECRET)

            if not os.path.isfile(Config.CRED_FILE):
                log.debug(f"{Config.CRED_FILE} does not exist")
                self.status = False
                self.message = "Upload failed: bot is not authenticated."
                return

            auth.LoadCredentialsFile(Config.CRED_FILE)

            google = await loop.run_in_executor(None, auth.authorize)

            # ✅ Category selection fixed
            if Config.VIDEO_CATEGORY in self.video_category:
                category_id = Config.VIDEO_CATEGORY
            else:
                category_id = random.choice(list(self.video_category.keys()))

            category_name = self.video_category[category_id]

            # ✅ Title handling
            title = self.title if self.title else os.path.basename(self.file)
            title = (
                (Config.VIDEO_TITLE_PREFIX + title + Config.VIDEO_TITLE_SUFFIX)
                .replace("<", "")
                .replace(">", "")
                .replace("|", "")
                .strip()[:100]
            )

            description = (
                Config.VIDEO_DESCRIPTION
                + "\nUploaded via Telegram Bot"
            )[:5000]

            privacy_status = Config.UPLOAD_MODE if Config.UPLOAD_MODE else "private"

            properties = dict(
                title=title,
                description=description,
                category=category_id,
                privacyStatus=privacy_status,
            )

            log.debug(f"Upload payload: {properties}")

            youtube = YouTube(google)

            response = await loop.run_in_executor(
    None,
    youtube.upload_video,
    self.file,
    properties,
    self.progress,
    *self.args
)

            log.debug(response)

            if not response or "id" not in response:
                self.status = False
                self.message = "Upload failed: invalid response from YouTube API."
                return

            video_id = response["id"]

            self.status = True
            self.message = (
                f"[{title}](https://youtu.be/{video_id}) uploaded successfully!\n"
                f"Category: {category_id} ({category_name})"
            )

        except Exception as e:
            log.error(e, exc_info=True)
            self.status = False
            self.message = f"Error occurred during upload.\nDetails: {e}"
