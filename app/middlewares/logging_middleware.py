from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from app.database import db


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, Message) and event.from_user:
            state = data.get("state")
            state_name = None

            if state:
                state_name = await state.get_state()

            db.log_action(
                user_id=event.from_user.id,
                chat_id=event.chat.id,
                username=event.from_user.username,
                full_name=event.from_user.full_name,
                action="message",
                message_text=event.text,
                state_name=state_name
            )

        return await handler(event, data)