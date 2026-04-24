from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards.reply import main_menu_kb
from app.strings import get_text

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()

    db.add_or_update_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    lang = db.get_user_lang(message.from_user.id)

    await message.answer(
        get_text(lang, "welcome"),
        reply_markup=main_menu_kb(lang)
    )


@router.message(F.text == "🔄 Restart")
async def restart_handler(message: types.Message, state: FSMContext):
    await state.clear()

    db.add_or_update_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    lang = db.get_user_lang(message.from_user.id)

    await message.answer(
        get_text(lang, "welcome"),
        reply_markup=main_menu_kb(lang)
    )