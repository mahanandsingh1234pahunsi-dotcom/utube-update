from pyrogram import filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..services.otp_service import generate_otp, verify_otp
from ..services.user_service import verify_user


@UtubeBot.on_message(filters.command("verify"))
async def verify(_, m: Message):
    otp = generate_otp(m.from_user.id)

    # ⚠️ In real app send via SMS/email
    await m.reply_text(f"🔐 Your OTP: {otp}")


@UtubeBot.on_message(filters.command("otp"))
async def otp_check(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("❌ Usage: /otp CODE")

    otp = int(m.command[1])

    if verify_otp(m.from_user.id, otp):
        verify_user(m.from_user.id)
        await m.reply_text("✅ Verified successfully!")
    else:
        await m.reply_text("❌ Invalid OTP")
