import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import BOT_TOKEN
from app.database import db
from app.middlewares.logging_middleware import LoggingMiddleware

from app.handlers.start import router as start_router
from app.handlers.language import router as language_router
from app.handlers.debt import router as debt_router
from app.handlers.reports import router as reports_router
from app.handlers.misc import router as misc_router
from app.handlers.admin import router as admin_router


async def main():
    logging.basicConfig(level=logging.INFO)

    db.init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(LoggingMiddleware())

    dp.include_router(start_router)
    dp.include_router(language_router)
    dp.include_router(debt_router)
    dp.include_router(reports_router)
    dp.include_router(admin_router)
    dp.include_router(misc_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())