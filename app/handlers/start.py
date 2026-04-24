from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards.reply import main_menu_kb, confirm_request_inline_kb
from app.strings import get_text

router = Router()


def build_pending_text(lang: str, row):
    debt_id, creator_id, person_name, amount, currency, direction, taken_at, due_at, note = row

    direction_text = {
        "uz": {"lent": "Qarz berdi", "borrowed": "Qarz oldi"},
        "en": {"lent": "Lent", "borrowed": "Borrowed"},
        "ru": {"lent": "Дал долг", "borrowed": "Взял долг"},
    }

    return (
        f"{get_text(lang, 'incoming_request')}\n\n"
        f"🆔 ID: {debt_id}\n"
        f"👤 {person_name}\n"
        f"💰 {amount} {currency}\n"
        f"🔄 {direction_text.get(lang, direction_text['uz']).get(direction, direction)}\n"
        f"📅 {taken_at}\n"
        f"⏰ {due_at or '-'}\n"
        f"📝 {note or '-'}"
    )


async def send_pending_requests(message: types.Message, lang: str):
    pending_rows = db.get_pending_debts_for_user(message.from_user.id)

    if not pending_rows:
        return

    for row in pending_rows:
        debt_id = row[0]
        await message.answer(
            build_pending_text(lang, row),
            reply_markup=confirm_request_inline_kb(debt_id, lang)
        )


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

    await send_pending_requests(message, lang)


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

    await send_pending_requests(message, lang)