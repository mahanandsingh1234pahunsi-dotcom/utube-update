import os
from pyrogram import Client

SESSIONS = {}
API_ID = 123456        # put in config later
API_HASH = "your_api_hash"


def get_session_name(user_id):
    return f"sessions/{user_id}"


def create_client(user_id: int):
    session = get_session_name(user_id)

    client = Client(
        session,
        api_id=API_ID,
        api_hash=API_HASH
    )

    SESSIONS[user_id] = client
    return client


def get_client(user_id: int):
    return SESSIONS.get(user_id)
