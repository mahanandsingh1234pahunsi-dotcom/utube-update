from pyrogram import StopTransmission, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

import os
import time
import string
import random
import logging
import asyncio
import datetime
from typing import Tuple, Union

from ..translations import Messages as tr
from ..helpers.downloader import Downloader
from ..helpers.uploader import Uploader
from ..services.fetch_service import fetch_video_from_link
from ..services.smart_fetch import smart_fetch   # ✅ NEW
from ..config import Config
from ..utubebot import UtubeBot


log = logging.getLogger(__name__)


@UtubeBot.on_message(
    filters.private
    & filters.incoming
    & filters.command("upload")
    & filters.user(Config.AUTH_USERS)
)
async def _upload(c: UtubeBot, m: Message):

    if not os.path.exists(Config.CRED_FILE):
        await m.reply_text(tr.NOT_AUTHENTICATED_MSG)
        return

    # =========================================================
    # ✅ CASE 1: TELEGRAM LINK IN COMMAND
    # =========================================================
    if len(m.command) > 1 and "t.me/" in m.command[1]:
        link = m.command[1]

        if c.counter >= 6:
            await m.reply_text(tr.DAILY_QOUTA_REACHED)
            return

        snt = await m.reply_text("📥 Fetching video from Telegram link...")
        c.counter += 1

        try:
            # ✅ SMART FETCH (AUTO PUBLIC + PRIVATE)
            file = await smart_fetch(link)

            await snt.edit_text("📤 Uploading to YouTube...")

            title = " ".join(m.command[2:]) if len(m.command) > 2 else "Uploaded via Bot"

            upload = Uploader(file, title)
            status, yt_link = await upload.start(progress, snt)

            if not status:
                c.counter = max(0, c.counter - 1)

            await snt.edit_text(yt_link, parse_mode=enums.ParseMode.HTML)

        except Exception as e:
            c.counter = max(0, c.counter - 1)

            if "LOGIN_REQUIRED" in str(e):
                await snt.edit_text(
                    "🔐 Private content detected!\n\n"
                    "Please login your Telegram account:\n"
                    "/tg_login PHONE_NUMBER"
                )
            else:
                await snt.edit_text(f"❌ Error:\n{e}")

        return

    # =========================================================
    # ✅ CASE 1.5: TELEGRAM LINK VIA REPLY (NEW 🔥)
    # =========================================================
    if m.reply_to_message and m.reply_to_message.text:
        text = m.reply_to_message.text

        if "t.me/" in text:
            link = text.strip()

            if c.counter >= 6:
                await m.reply_text(tr.DAILY_QOUTA_REACHED)
                return

            snt = await m.reply_text("📥 Fetching video...")
            c.counter += 1

            try:
                file = await smart_fetch(link)

                await snt.edit_text("📤 Uploading to YouTube...")

                title = " ".join(m.command[1:]) if len(m.command) > 1 else "Uploaded via Bot"

                upload = Uploader(file, title)
                status, yt_link = await upload.start(progress, snt)

                if not status:
                    c.counter = max(0, c.counter - 1)

                await snt.edit_text(yt_link, parse_mode=enums.ParseMode.HTML)

            except Exception as e:
                c.counter = max(0, c.counter - 1)

                if "LOGIN_REQUIRED" in str(e):
                    await snt.edit_text(
                        "🔐 Private content detected!\n\n"
                        "Please login your Telegram account:\n"
                        "/tg_login PHONE_NUMBER"
                    )
                else:
                    await snt.edit_text(f"❌ Error:\n{e}")

            return

    # =========================================================
    # ✅ CASE 2: REPLY MEDIA (OLD SYSTEM - UNTOUCHED)
    # =========================================================
    if not m.reply_to_message:
        await m.reply_text(tr.NOT_A_REPLY_MSG)
        return

    message = m.reply_to_message

    if not message.media:
        await m.reply_text(tr.NOT_A_MEDIA_MSG)
        return

    if not valid_media(message):
        await m.reply_text(tr.NOT_A_VALID_MEDIA_MSG)
        return

    if c.counter >= 6:
        await m.reply_text(tr.DAILY_QOUTA_REACHED)
        return

    snt = await m.reply_text(tr.PROCESSING)
    c.counter += 1

    download_id = get_download_id(c.download_controller)
    c.download_controller[download_id] = True

    download = Downloader(m)
    status, file = await download.start(progress, snt, c, download_id)

    log.debug(f"{status}, {file}")
    c.download_controller.pop(download_id)

    if not status:
        c.counter = max(0, c.counter - 1)
        await snt.edit_text(text=file)
        return

    try:
        await snt.edit_text("Downloaded. Now uploading to YouTube...")
    except Exception as e:
        log.warning(e, exc_info=True)

    title = " ".join(m.command[1:]) if len(m.command) > 1 else "Uploaded via Bot"

    upload = Uploader(file, title)
    status, yt_link = await upload.start(progress, snt)

    log.debug(f"{status}, {yt_link}")

    if not status:
        c.counter = max(0, c.counter - 1)

    try:
        await snt.edit_text(
            text=yt_link,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        log.warning(f"Final message failed: {e}")
        await snt.edit_text(text=str(yt_link))


# ================= HELPERS =================

def get_download_id(storage: dict) -> str:
    while True:
        download_id = "".join(random.choice(string.ascii_letters) for _ in range(3))
        if download_id not in storage:
            return download_id


def valid_media(media: Message) -> bool:
    return bool(
        media.video
        or media.video_note
        or media.animation
        or (media.document and "video" in media.document.mime_type)
    )


def human_bytes(
    num: Union[int, float], split: bool = False
) -> Union[str, Tuple[int, str]]:
    base = 1024.0
    sufix_list = ["B", "KB", "MB", "GB", "TB"]

    for unit in sufix_list:
        if abs(num) < base:
            return (round(num, 2), unit) if split else f"{round(num, 2)} {unit}"
        num /= base


async def progress(
    cur: Union[int, float],
    tot: Union[int, float],
    start_time: float,
    status: str,
    snt: Message,
    c: UtubeBot,
    download_id: str,
):
    if not c.download_controller.get(download_id):
        raise StopTransmission

    try:
        diff = int(time.time() - start_time) or 1

        if (int(time.time()) % 5 == 0) or (cur == tot):
            await asyncio.sleep(1)

            speed, unit = human_bytes(cur / diff, True)
            curr = human_bytes(cur)
            tott = human_bytes(tot)

            eta = datetime.timedelta(
                seconds=int(((tot - cur) / (1024 * 1024)) / max(speed, 1))
            )
            elapsed = datetime.timedelta(seconds=diff)
            progress_percent = round((cur * 100) / tot, 2)

            text = (
                f"{status}\n\n"
                f"{progress_percent}% done\n"
                f"{curr} of {tott}\n"
                f"Speed: {speed} {unit}/s\n"
                f"ETA: {eta}\n"
                f"Elapsed: {elapsed}"
            )

            await snt.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Cancel!", callback_data=f"cncl+{download_id}"
                            )
                        ]
                    ]
                ),
            )

    except Exception as e:
        log.info(e)
