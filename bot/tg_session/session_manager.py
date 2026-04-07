# bot/tg_session/session_manager.py

import os
from telethon import TelegramClient
from telethon.sessions import StringSession

from ..config import Config

SESSION_DIR = "bot/sessions"


class SessionManager:

    def __init__(self):
        self.clients = {}
        os.makedirs(SESSION_DIR, exist_ok=True)

    # ================= START / LOAD SESSION =================

    async def start(self, user_id: int):

        session_file = f"{SESSION_DIR}/{user_id}.txt"

        if not os.path.exists(session_file):
            return None

        # Return cached client
        if user_id in self.clients:
            return self.clients[user_id]

        try:
            with open(session_file, "r") as f:
                session_str = f.read().strip()

            if not session_str:
                return None

            client = TelegramClient(
                StringSession(session_str),
                Config.API_ID,
                Config.API_HASH
            )

            await client.start()

            self.clients[user_id] = client
            return client

        except Exception:
            return None

    # ================= SAVE SESSION =================

    async def save(self, user_id: int, session_str: str):

        session_file = f"{SESSION_DIR}/{user_id}.txt"

        with open(session_file, "w") as f:
            f.write(session_str.strip())

        return True

    # ================= CHECK SESSION =================

    def has_session(self, user_id: int):

        session_file = f"{SESSION_DIR}/{user_id}.txt"
        return os.path.exists(session_file)

    # ================= LOGOUT =================

    async def logout(self, user_id: int):

        session_file = f"{SESSION_DIR}/{user_id}.txt"

        if user_id in self.clients:
            try:
                await self.clients[user_id].disconnect()
            except:
                pass
            del self.clients[user_id]

        if os.path.exists(session_file):
            os.remove(session_file)

        return True
