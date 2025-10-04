from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.config import settings
from app.repositories.message_repository import MessageRepository
from app.schemas.tg_update import TelegramUpdate, TelegramMessage


class MessageService:
    def __init__(self, session: AsyncSession):
        self._messages = MessageRepository(session)

    async def add(self, message: TelegramMessage):
        return await self._messages.add(message)