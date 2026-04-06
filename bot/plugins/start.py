from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from ..translations import Messages as tr
from ..config import Config
from ..utubebot import UtubeBot


@UtubeBot.on_message(
    filters.private
    & filters.incoming
    & filters.command("start")
    & filters.user(Config.AUTH_USERS)
)
async def _start(c: UtubeBot, m: Message):
    await c.send_chat_action(m.chat.id, enums.ChatAction.TYPING)

    await m.reply_text(
        text=tr.START_MSG.format(m.from_user.first_name),
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Project Channel!", url="https://t.me/odbots")]]
        ),
    )
