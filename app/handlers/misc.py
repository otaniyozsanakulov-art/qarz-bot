from aiogram import Router, types

from app.database import db
from app.keyboards.reply import main_menu_kb
from app.strings import get_text

router = Router()


@router.message()
async def fallback_handler(message: types.Message):
    db.add_or_update_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    lang = db.get_user_lang(message.from_user.id)

    await message.answer(
        get_text(lang, "unknown_command"),
        reply_markup=main_menu_kb(lang)
    )