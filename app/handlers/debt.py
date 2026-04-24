from datetime import datetime, timedelta

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database import db
from app.filters import normalize_currency, normalize_direction
from app.keyboards.reply import (
    main_menu_kb,
    currency_kb,
    debt_type_kb,
    save_type_kb,
    confirm_request_inline_kb,
    due_date_kb,
    taken_date_kb
)
from app.states.debt_states import DebtState
from app.strings import get_text

router = Router()


def valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except Exception:
        return False


def build_request_text(lang: str, creator_name: str, data: dict):
    direction_label = {
        "uz": {"lent": "Berdi", "borrowed": "Oldi"},
        "en": {"lent": "Lent", "borrowed": "Borrowed"},
        "ru": {"lent": "Дал", "borrowed": "Взял"},
    }

    return (
        f"{get_text(lang, 'incoming_request')}\n\n"
        f"👤 {creator_name}\n"
        f"🧾 {data['person_name']}\n"
        f"💰 {data['amount']} {data['currency']}\n"
        f"🔄 {direction_label[lang][data['direction']]}\n"
        f"📅 {data['taken_at']}\n"
        f"⏰ {data['due_at'] or '-'}\n"
        f"📝 {data['note'] or '-'}"
    )


@router.message(F.text.in_(["➕ Yangi qarz yozish", "➕ Add new debt", "➕ Добавить долг"]))
async def start_debt(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    await state.clear()
    await message.answer(get_text(lang, "enter_name"))
    await state.set_state(DebtState.entering_name)


@router.message(F.text.in_(["❌ Bekor qilish", "❌ Cancel", "❌ Отмена"]))
async def cancel_anywhere(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    await state.clear()
    await message.answer(get_text(lang, "cancelled"), reply_markup=main_menu_kb(lang))


@router.message(DebtState.entering_name)
async def process_name(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    await state.update_data(person_name=message.text.strip())
    await message.answer(get_text(lang, "enter_amount"))
    await state.set_state(DebtState.entering_amount)


@router.message(DebtState.entering_amount)
async def process_amount(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)

    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError

        await state.update_data(amount=amount)
        await message.answer(get_text(lang, "choose_currency"), reply_markup=currency_kb(lang))
        await state.set_state(DebtState.choosing_currency)

    except ValueError:
        await message.answer(get_text(lang, "enter_amount_error"))


@router.message(DebtState.choosing_currency)
async def process_currency(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    currency = normalize_currency(message.text)

    if currency not in ("UZS", "USD", "RUB"):
        await message.answer(get_text(lang, "choose_currency"), reply_markup=currency_kb(lang))
        return

    await state.update_data(currency=currency)
    await message.answer(get_text(lang, "choose_type"), reply_markup=debt_type_kb(lang))
    await state.set_state(DebtState.choosing_type)


@router.message(DebtState.choosing_type)
async def process_type(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    direction = normalize_direction(message.text)

    if direction not in ("lent", "borrowed"):
        await message.answer(get_text(lang, "choose_type"), reply_markup=debt_type_kb(lang))
        return

    await state.update_data(direction=direction)
    await message.answer(
        get_text(lang, "enter_taken_date"),
        reply_markup=taken_date_kb(lang)
    )
    await state.set_state(DebtState.entering_taken_date)

@router.message(DebtState.entering_taken_date)
async def process_taken_date(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    text = message.text.strip()

    if text == get_text(lang, "due_today"):
        taken_at = str(datetime.now().date())
    else:
        if not valid_date(text):
            await message.answer(
                get_text(lang, "enter_taken_date_error"),
                reply_markup=taken_date_kb(lang)
            )
            return
        taken_at = text

    await state.update_data(taken_at=taken_at)
    await message.answer(
        get_text(lang, "choose_due_date_fast"),
        reply_markup=due_date_kb(lang)
    )
    await state.set_state(DebtState.entering_due_date)


@router.message(DebtState.entering_due_date)
async def process_due_date(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    text = message.text.strip()

    today = datetime.now().date()

    if text == get_text(lang, "due_today"):
        due_at = str(today)
    elif text == get_text(lang, "due_tomorrow"):
        due_at = str(today + timedelta(days=1))
    elif text == get_text(lang, "due_3_days"):
        due_at = str(today + timedelta(days=3))
    elif text == get_text(lang, "due_7_days"):
        due_at = str(today + timedelta(days=7))
    elif text == get_text(lang, "due_15_days"):
        due_at = str(today + timedelta(days=15))
    elif text == get_text(lang, "due_30_days"):
        due_at = str(today + timedelta(days=30))
    elif text == get_text(lang, "due_no_limit"):
        due_at = None
    else:
        await message.answer(
            get_text(lang, "choose_due_date_fast"),
            reply_markup=due_date_kb(lang)
        )
        return

    await state.update_data(due_at=due_at)
    await message.answer(get_text(lang, "enter_note"))
    await state.set_state(DebtState.entering_note)


@router.message(DebtState.entering_note)
async def process_note(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    text = message.text.strip()

    await state.update_data(note=None if text == "-" else text)
    await message.answer(get_text(lang, "confirm_save"), reply_markup=save_type_kb(lang))
    await state.set_state(DebtState.choosing_save_type)


@router.message(DebtState.choosing_save_type)
async def process_save_type(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)

    if message.text == get_text(lang, "save_only_me"):
        data = await state.get_data()

        db.save_debt(
            creator_id=message.from_user.id,
            person_name=data["person_name"],
            amount=data["amount"],
            currency=data["currency"],
            direction=data["direction"],
            taken_at=data["taken_at"],
            due_at=data["due_at"],
            note=data["note"],
            confirmation_status="self_saved"
        )

        await state.clear()
        await message.answer(get_text(lang, "saved"), reply_markup=main_menu_kb(lang))
        return

    if message.text == get_text(lang, "send_for_confirm"):
        await message.answer(get_text(lang, "enter_other_username"))
        await state.set_state(DebtState.entering_other_username)
        return

    await message.answer(get_text(lang, "confirm_save"), reply_markup=save_type_kb(lang))


@router.message(DebtState.entering_other_username)
async def process_other_username(message: types.Message, state: FSMContext, bot: Bot):
    lang = db.get_user_lang(message.from_user.id)

    username = message.text.strip().lstrip("@")

    if not username:
        await message.answer(get_text(lang, "enter_other_username"))
        return

    second_user = db.get_user_by_username(username)

    if not second_user:
        await message.answer(get_text(lang, "username_not_found"))
        return

    second_user_id, second_full_name, second_username, second_lang = second_user

    if second_user_id == message.from_user.id:
        await message.answer(get_text(lang, "cannot_send_self"))
        return

    data = await state.get_data()

    debt_id = db.save_debt(
        creator_id=message.from_user.id,
        person_name=data["person_name"],
        amount=data["amount"],
        currency=data["currency"],
        direction=data["direction"],
        taken_at=data["taken_at"],
        due_at=data["due_at"],
        note=data["note"],
        second_party_user_id=second_user_id,
        second_party_username=second_username,
        confirmation_status="pending"
    )

    try:
        await bot.send_message(
            chat_id=second_user_id,
            text=build_request_text(
                second_lang,
                message.from_user.full_name,
                data
            ),
            reply_markup=confirm_request_inline_kb(debt_id, second_lang)
        )
    except Exception:
        await message.answer(get_text(lang, "username_not_found"))
        return

    await state.clear()
    await message.answer(get_text(lang, "sent_for_confirmation"), reply_markup=main_menu_kb(lang))


@router.callback_query(F.data.startswith("confirm_debt:"))
async def confirm_debt_callback(callback: CallbackQuery):
    debt_id = int(callback.data.split(":")[1])
    debt = db.get_debt_by_id(debt_id)

    if not debt:
        await callback.answer("Not found", show_alert=True)
        return

    _, creator_id, second_party_user_id, _, _, _, _, _, _, _, _, _, confirmation_status = debt

    if callback.from_user.id != second_party_user_id:
        await callback.answer("Bu so'rov sizniki emas.", show_alert=True)
        return

    if confirmation_status != "pending":
        await callback.answer("Bu so'rov allaqachon yakunlangan.", show_alert=True)
        return

    db.update_confirmation_status(debt_id, "confirmed")

    user_lang = db.get_user_lang(callback.from_user.id)
    creator_lang = db.get_user_lang(creator_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(get_text(user_lang, "you_confirmed"))

    try:
        await callback.bot.send_message(
            chat_id=creator_id,
            text=get_text(creator_lang, "request_confirmed")
        )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(F.data.startswith("reject_debt:"))
async def reject_debt_callback(callback: CallbackQuery):
    debt_id = int(callback.data.split(":")[1])
    debt = db.get_debt_by_id(debt_id)

    if not debt:
        await callback.answer("Not found", show_alert=True)
        return

    _, creator_id, second_party_user_id, _, _, _, _, _, _, _, _, _, confirmation_status = debt

    if callback.from_user.id != second_party_user_id:
        await callback.answer("Bu so'rov sizniki emas.", show_alert=True)
        return

    if confirmation_status != "pending":
        await callback.answer("Bu so'rov allaqachon yakunlangan.", show_alert=True)
        return

    db.update_confirmation_status(debt_id, "rejected")

    user_lang = db.get_user_lang(callback.from_user.id)
    creator_lang = db.get_user_lang(creator_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(get_text(user_lang, "you_rejected"))

    try:
        await callback.bot.send_message(
            chat_id=creator_id,
            text=get_text(creator_lang, "request_rejected")
        )
    except Exception:
        pass

    await callback.answer()