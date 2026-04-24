from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.strings import get_text


def language_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha")],
            [KeyboardButton(text="🇬🇧 English")],
            [KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )


def main_menu_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "main_add"))],
            [KeyboardButton(text=get_text(lang, "main_report"))],
            [KeyboardButton(text=get_text(lang, "main_language"))],
            [KeyboardButton(text=get_text(lang, "main_restart"))],
        ],
        resize_keyboard=True
    )


def currency_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 UZS")],
            [KeyboardButton(text="🇺🇸 USD")],
            [KeyboardButton(text="🇷🇺 RUB")],
            [KeyboardButton(text=get_text(lang, "main_cancel"))],
        ],
        resize_keyboard=True
    )


def debt_type_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "type_lent"))],
            [KeyboardButton(text=get_text(lang, "type_borrowed"))],
            [KeyboardButton(text=get_text(lang, "main_cancel"))],
        ],
        resize_keyboard=True
    )


def due_date_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "due_today")), KeyboardButton(text=get_text(lang, "due_tomorrow"))],
            [KeyboardButton(text=get_text(lang, "due_3_days")), KeyboardButton(text=get_text(lang, "due_7_days"))],
            [KeyboardButton(text=get_text(lang, "due_15_days")), KeyboardButton(text=get_text(lang, "due_30_days"))],
            [KeyboardButton(text=get_text(lang, "due_no_limit"))],
            [KeyboardButton(text=get_text(lang, "main_cancel"))],
        ],
        resize_keyboard=True
    )


def save_type_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "save_only_me"))],
            [KeyboardButton(text=get_text(lang, "send_for_confirm"))],
            [KeyboardButton(text=get_text(lang, "main_cancel"))],
        ],
        resize_keyboard=True
    )


def confirm_request_inline_kb(debt_id: int, lang: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(lang, "confirm_btn"),
                    callback_data=f"confirm_debt:{debt_id}"
                ),
                InlineKeyboardButton(
                    text=get_text(lang, "reject_btn"),
                    callback_data=f"reject_debt:{debt_id}"
                ),
            ]
        ]
    )
def report_direction_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "report_lent_filter"))],
            [KeyboardButton(text=get_text(lang, "report_borrowed_filter"))],
            [KeyboardButton(text=get_text(lang, "main_restart"))],
        ],
        resize_keyboard=True
    )


def report_type_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "report_full"))],
            [KeyboardButton(text=get_text(lang, "report_search"))],
            [KeyboardButton(text=get_text(lang, "main_restart"))],
        ],
        resize_keyboard=True
    )
def taken_date_kb(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, "due_today"))],
            [KeyboardButton(text=get_text(lang, "main_cancel"))],
        ],
        resize_keyboard=True
    )