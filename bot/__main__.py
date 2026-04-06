import logging

from pyrogram import idle  # ✅ IMPORTANT

from .utubebot import UtubeBot
from .config import Config


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if Config.DEBUG else logging.INFO)
    logging.getLogger("pyrogram").setLevel(
        logging.INFO if Config.DEBUG else logging.WARNING
    )

    bot = UtubeBot()
    bot.start()

    print("Bot is running...")

    idle()   # ✅ correct usage

    bot.stop()
