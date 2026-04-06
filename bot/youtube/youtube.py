import time
import random
import logging
import os
import asyncio

from httplib2 import HttpLib2Error
from http.client import (
    NotConnected,
    IncompleteRead,
    ImproperConnectionState,
    CannotSendRequest,
    CannotSendHeader,
    ResponseNotReady,
    BadStatusLine,
)

from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import Resource


log = logging.getLogger(__name__)


class MaxRetryExceeded(Exception):
    pass


class UploadFailed(Exception):
    pass


class YouTube:

    MAX_RETRIES = 10

    RETRIABLE_EXCEPTIONS = (
        HttpLib2Error,
        IOError,
        NotConnected,
        IncompleteRead,
        ImproperConnectionState,
        CannotSendRequest,
        CannotSendHeader,
        ResponseNotReady,
        BadStatusLine,
    )

    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    def __init__(self, auth: Resource, chunksize: int = -1):
        self.youtube = auth
        self.request = None
        self.chunksize = chunksize
        self.response = None
        self.error = None
        self.retry = 0

    def upload_video(
        self, video: str, properties: dict, progress: callable = None, *args
    ) -> dict:

        self.progress = progress
        self.progress_args = args
        self.video = video
        self.properties = properties

        body = dict(
            snippet=dict(
                title=self.properties.get("title"),
                description=self.properties.get("description"),
                categoryId=self.properties.get("category"),
            ),
            status=dict(
                privacyStatus=self.properties.get("privacyStatus")
            ),
        )

        media_body = MediaFileUpload(
            self.video,
            chunksize=self.chunksize,
            resumable=True,
        )

        self.request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media_body,
        )

        self._resumable_upload()
        return self.response

    def _resumable_upload(self) -> dict:
        response = None

        start_time = time.time()
        total_size = os.path.getsize(self.video)

        while response is None:
            try:
                status, response = self.request.next_chunk()

                # ✅ UPLOAD PROGRESS
                if status and self.progress:
                    try:
                        progress_float = status.progress()

                        uploaded_bytes = int(progress_float * total_size)
                        total_bytes = total_size

                        now = time.time()
                        diff = now - start_time or 1

                        speed = uploaded_bytes / diff  # bytes/sec
                        remaining = total_bytes - uploaded_bytes
                        eta = remaining / speed if speed > 0 else 0

                        coro = self.progress(
                            uploaded_bytes,
                            total_bytes,
                            start_time,
                            "Uploading...",
                            *self.progress_args
                        )

                        loop = asyncio.get_event_loop()

                        if loop.is_running():
                            loop.create_task(coro)
                        else:
                            asyncio.run(coro)

                    except Exception as e:
                        log.debug(f"Progress error: {e}")

                # ✅ FINAL RESPONSE
                if response is not None:
                    if "id" in response:
                        self.response = response
                    else:
                        raise UploadFailed(f"Unexpected response: {response}")

            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    self.error = (
                        f"HTTP error {e.resp.status}: {e.content}"
                    )
                else:
                    raise

            except self.RETRIABLE_EXCEPTIONS as e:
                self.error = f"Error: {e}"

            if self.error:
                log.debug(self.error)
                self.retry += 1

                if self.retry > self.MAX_RETRIES:
                    raise MaxRetryExceeded("Max retries exceeded.")

                sleep_seconds = random.random() * (2 ** self.retry)
                log.debug(f"Retrying in {sleep_seconds:.2f}s...")
                time.sleep(sleep_seconds)


def print_response(response: dict) -> None:
    for key, value in response.items():
        print(f"{key}: {value}\n")
