from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from saver_app.core.config import settings
from saver_app.repositories.message_repository import MessageRepository
from saver_app.schemas.tg_update import TelegramUpdate, TelegramMessage


class MessageService:
    def __init__(self, session: AsyncSession):
        self._messages = MessageRepository(session)

    async def add(self, message: TelegramMessage):
        return await self._messages.add(message)