from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.database import db
from app.keyboards.reply import main_menu_kb, report_direction_kb, report_type_kb
from app.states.debt_states import ReportState
from app.strings import get_text

router = Router()


def status_text(lang: str, status: str):
    mapping = {
        "self_saved": f"🔵 {get_text(lang, 'status_confirmed')}",
        "pending": f"🟡 {get_text(lang, 'status_pending')}",
        "confirmed": f"🟢 {get_text(lang, 'status_confirmed')}",
        "rejected": f"🔴 {get_text(lang, 'status_rejected')}",
    }
    return mapping.get(status, status)


def format_report_rows(lang: str, rows):
    if not rows:
        return get_text(lang, "report_empty")

    text = ""
    for row in rows:
        person_name, amount, currency, taken_at, due_at, note, confirmation_status = row
        text += (
            f"👤 {person_name}\n"
            f"💰 {amount} {currency}\n"
            f"📅 {taken_at}\n"
            f"⏰ {due_at or '-'}\n"
            f"📝 {note or '-'}\n"
            f"📌 {status_text(lang, confirmation_status)}\n\n"
        )
    return text


def get_direction_from_button(lang: str, text: str):
    if text == get_text(lang, "report_lent_filter"):
        return "lent"
    if text == get_text(lang, "report_borrowed_filter"):
        return "borrowed"
    return None


@router.message(F.text.in_(["📊 Umumiy hisobot", "📊 General report", "📊 Общий отчет"]))
async def report_start(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)

    await state.clear()
    await message.answer(
        get_text(lang, "report_choose_direction"),
        reply_markup=report_direction_kb(lang)
    )
    await state.set_state(ReportState.choosing_direction)


@router.message(ReportState.choosing_direction)
async def report_choose_direction(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    direction = get_direction_from_button(lang, message.text)

    if not direction:
        await message.answer(
            get_text(lang, "report_choose_direction"),
            reply_markup=report_direction_kb(lang)
        )
        return

    await state.update_data(report_direction=direction)
    await message.answer(
        get_text(lang, "report_choose_type"),
        reply_markup=report_type_kb(lang)
    )
    await state.set_state(ReportState.choosing_type)


@router.message(ReportState.choosing_type)
async def report_choose_type(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    data = await state.get_data()
    direction = data["report_direction"]

    if message.text == get_text(lang, "report_full"):
        rows = db.get_open_debts_by_direction(message.from_user.id, direction)

        title = get_text(lang, "report_lent") if direction == "lent" else get_text(lang, "report_borrowed")
        text = f"{title}\n\n{format_report_rows(lang, rows)}"

        await state.clear()
        await message.answer(text, reply_markup=main_menu_kb(lang))
        return

    if message.text == get_text(lang, "report_search"):
        await message.answer(get_text(lang, "report_enter_search"))
        await state.set_state(ReportState.entering_search)
        return

    await message.answer(
        get_text(lang, "report_choose_type"),
        reply_markup=report_type_kb(lang)
    )


@router.message(ReportState.entering_search)
async def report_search(message: types.Message, state: FSMContext):
    lang = db.get_user_lang(message.from_user.id)
    data = await state.get_data()
    direction = data["report_direction"]

    rows = db.search_open_debts(
        user_id=message.from_user.id,
        direction=direction,
        search_text=message.text
    )

    title = get_text(lang, "report_lent") if direction == "lent" else get_text(lang, "report_borrowed")

    if not rows:
        text = get_text(lang, "report_no_result")
    else:
        text = f"{title}\n\n{format_report_rows(lang, rows)}"

    await state.clear()
    await message.answer(text, reply_markup=main_menu_kb(lang))