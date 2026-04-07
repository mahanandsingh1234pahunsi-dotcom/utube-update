import os
from telethon import TelegramClient
from telethon.sessions import StringSession

from ..config import Config

SESSION_FILE = "tg_session.txt"


class SessionManager:

    def __init__(self):
        self.client = None

    async def start(self):
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                session = f.read().strip()

            self.client = TelegramClient(
                StringSession(session),
                Config.API_ID,
                Config.API_HASH
            )
            await self.client.start()
            return True

        return False

    async def login(self, phone):
        self.client = TelegramClient(
            StringSession(),
            Config.API_ID,
            Config.API_HASH
        )
        await self.client.connect()
        await self.client.send_code_request(phone)

    async def verify(self, phone, code):
        await self.client.sign_in(phone, code)

        session_str = self.client.session.save()

        with open(SESSION_FILE, "w") as f:
            f.write(session_str)

        return True
