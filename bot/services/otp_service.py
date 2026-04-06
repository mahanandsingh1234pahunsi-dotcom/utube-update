import random

otp_storage = {}


def generate_otp(user_id: int) -> int:
    otp = random.randint(100000, 999999)
    otp_storage[user_id] = otp
    return otp


def verify_otp(user_id: int, otp: int) -> bool:
    return otp_storage.get(user_id) == otp
