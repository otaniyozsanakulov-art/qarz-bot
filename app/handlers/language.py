from aiogram import Router, types, F

from app.database import db
from app.keyboards.reply import language_kb, main_menu_kb
from app.strings import get_text

router = Router()


@router.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Change language", "🌐 Изменить язык"]))
async def change_language_menu(message: types.Message):
    await message.answer(
        "Tilni tanlang / Choose language / Выберите язык:",
        reply_markup=language_kb()
    )


@router.message(F.text == "🇺🇿 O'zbekcha")
async def set_lang_uz(message: types.Message):
    db.add_or_update_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )
    db.set_user_lang(message.from_user.id, "uz")

    await message.answer(
        get_text("uz", "changed_language"),
        reply_markup=main_menu_kb("uz")
    )


@router.message(F.text == "🇬🇧 English")
async def set_lang_en(message: types.Message):
    db.add_or_update_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )
    db.set_user_lang(message.from_user.id, "en")

    await message.answer(
        get_text("en", "changed_language"),
        reply_markup=main_menu_kb("en")
    )


@router.message(F.text == "🇷🇺 Русский")
async def set_lang_ru(message: types.Message):
    db.add_or_update_user(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )
    db.set_user_lang(message.from_user.id, "ru")

    await message.answer(
        get_text("ru", "changed_language"),
        reply_markup=main_menu_kb("ru")
    )