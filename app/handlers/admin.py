from aiogram import Router, types, F
from aiogram.filters import Command

from app.config import ADMIN_ID
from app.database import db

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    stats = db.get_admin_stats()

    text = (
        "👑 Admin panel\n\n"
        f"👥 Foydalanuvchilar: {stats['users_count']}\n"
        f"🧾 Qarz yozuvlari: {stats['debts_count']}\n"
        f"🟡 Kutilayotganlar: {stats['pending_count']}\n"
        f"🟢 Tasdiqlanganlar: {stats['confirmed_count']}\n"
        f"🔴 Rad etilganlar: {stats['rejected_count']}\n"
        f"🕵️ Audit loglar: {stats['logs_count']}\n\n"
        "Buyruqlar:\n"
        "/users - oxirgi foydalanuvchilar\n"
        "/logs - oxirgi harakatlar"
    )

    await message.answer(text)


@router.message(Command("users"))
async def show_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    users = db.get_last_users(10)

    if not users:
        await message.answer("Foydalanuvchilar yo'q.")
        return

    text = "👥 Oxirgi foydalanuvchilar:\n\n"

    for user_id, full_name, username, language, created_at in users:
        text += (
            f"🆔 {user_id}\n"
            f"👤 {full_name}\n"
            f"🔗 @{username if username else '-'}\n"
            f"🌐 {language}\n"
            f"📅 {created_at}\n\n"
        )

    await message.answer(text)


@router.message(Command("logs"))
async def show_logs(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return

    logs = db.get_last_logs(10)

    if not logs:
        await message.answer("Loglar yo'q.")
        return

    text = "🕵️ Oxirgi harakatlar:\n\n"

    for user_id, username, full_name, message_text, state_name, created_at in logs:
        text += (
            f"🆔 {user_id}\n"
            f"👤 {full_name}\n"
            f"🔗 @{username if username else '-'}\n"
            f"💬 {message_text}\n"
            f"📌 State: {state_name}\n"
            f"📅 {created_at}\n\n"
        )

    await message.answer(text)