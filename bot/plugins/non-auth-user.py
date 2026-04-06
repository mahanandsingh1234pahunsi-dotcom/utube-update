import logging

from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..config import Config


log = logging.getLogger(__name__)


@UtubeBot.on_message(
    filters.private & filters.incoming & ~filters.user(Config.AUTH_USERS)
)
async def _non_auth_usr_msg(c: UtubeBot, m: Message):
    await m.delete()
    log.info(
        f"{Config.AUTH_USERS} Unauthorised user {m.chat.id} contacted. Message deleted."
    )
