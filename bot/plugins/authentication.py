import logging

from pyrogram import filters
from pyrogram.types import Message

from ..youtube import GoogleAuth
from ..config import Config
from ..translations import Messages as tr
from ..utubebot import UtubeBot


log = logging.getLogger(__name__)


@UtubeBot.on_message(
    filters.private
    & filters.incoming
    & filters.command("authorise")
    & filters.user(Config.AUTH_USERS)
)
async def _auth(c: UtubeBot, m: Message) -> None:

    if len(m.command) < 2:
        await m.reply_text(tr.NO_AUTH_CODE_MSG)
        return

    code = m.command[1]

    try:
        auth = GoogleAuth(Config.CLIENT_ID, Config.CLIENT_SECRET)

        auth.Auth(code)
        auth.SaveCredentialsFile(Config.CRED_FILE)

        msg = await m.reply_text(tr.AUTH_SUCCESS_MSG)

        with open(Config.CRED_FILE, "r") as f:
            cred_data = f.read()

        log.debug(f"Authentication success, saved to {Config.CRED_FILE}")

        msg2 = await msg.reply_text(cred_data, parse_mode=None)

        await msg2.reply_text(
            "This is your authorization data! Save this safely.\n"
            "Reply /save_auth_data to this message to restore later."
        )

    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(tr.AUTH_FAILED_MSG.format(e))


@UtubeBot.on_message(
    filters.private
    & filters.incoming
    & filters.command("save_auth_data")
    & filters.reply
    & filters.user(Config.AUTH_USERS)
)
async def _save_auth_data(c: UtubeBot, m: Message) -> None:

    auth_data = m.reply_to_message.text

    try:
        with open(Config.CRED_FILE, "w") as f:
            f.write(auth_data)

        auth = GoogleAuth(Config.CLIENT_ID, Config.CLIENT_SECRET)
        auth.LoadCredentialsFile(Config.CRED_FILE)
        auth.authorize()

        await m.reply_text(tr.AUTH_DATA_SAVE_SUCCESS)

        log.debug(f"Auth restored from {Config.CRED_FILE}")

    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(tr.AUTH_FAILED_MSG.format(e))
