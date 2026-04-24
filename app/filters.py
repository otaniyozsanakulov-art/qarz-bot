from app.strings import TEXTS

SUPPORTED_LANGS = ("uz", "en", "ru")


def normalize_currency(text: str) -> str:
    text = text.strip()

    if "SO'M" in text or "UZS" in text:
        return "UZS"
    if "USD" in text:
        return "USD"
    if "RUB" in text:
        return "RUB"

    return text


def normalize_direction(text: str) -> str:
    mapping = {
        TEXTS["uz"]["type_lent"]: "lent",
        TEXTS["uz"]["type_borrowed"]: "borrowed",
        TEXTS["en"]["type_lent"]: "lent",
        TEXTS["en"]["type_borrowed"]: "borrowed",
        TEXTS["ru"]["type_lent"]: "lent",
        TEXTS["ru"]["type_borrowed"]: "borrowed",
    }
    return mapping.get(text, text)