# bot/tg_session/session_manager.py

import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError
)

from ..config import Config

SESSION_FILE = "tg_session.txt"


class SessionManager:

    def __init__(self):
        self.client = None
        self.phone = None

    # ================= START SESSION =================

    async def start(self):
        """Start existing session"""
        if not os.path.exists(SESSION_FILE):
            return False

        try:
            with open(SESSION_FILE, "r") as f:
                session = f.read().strip()

            if not session:
                return False

            self.client = TelegramClient(
                StringSession(session),
                Config.API_ID,
                Config.API_HASH
            )

            await self.client.start()
            return True

        except Exception:
            return False

    # ================= LOGIN =================

    async def login(self, phone: str):
        """Send OTP"""
        self.phone = phone

        if self.client:
            await self.client.disconnect()

        self.client = TelegramClient(
            StringSession(),
            Config.API_ID,
            Config.API_HASH
        )

        await self.client.connect()

        try:
            await self.client.send_code_request(phone)
            return True

        except Exception as e:
            raise Exception(f"Failed to send OTP: {e}")

    # ================= VERIFY OTP =================

    async def verify(self, code: str):
        """Verify OTP and save session"""

        if not self.client or not self.phone:
            raise Exception("Login not initiated")

        try:
            await self.client.sign_in(self.phone, code)

        except PhoneCodeInvalidError:
            raise Exception("Invalid OTP")

        except PhoneCodeExpiredError:
            raise Exception("OTP expired")

        except SessionPasswordNeededError:
            raise Exception("2FA enabled. Not supported yet")

        # Save session
        session_str = self.client.session.save()

        with open(SESSION_FILE, "w") as f:
            f.write(session_str)

        return True

    # ================= GET CLIENT =================

    async def get_client(self):
        """Ensure client is ready"""
        if self.client:
            return self.client

        started = await self.start()
        if not started:
            return None

        return self.client

    # ================= LOGOUT =================

    async def logout(self):
        """Delete session"""
        if self.client:
            await self.client.disconnect()

        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        self.client = None
        self.phone = None

        return True
