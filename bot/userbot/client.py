from telethon import TelegramClient
from ..config import Config

# 👤 USERBOT CLIENT
userbot = TelegramClient(
    "userbot_session",
    Config.API_ID,
    Config.API_HASH
)
