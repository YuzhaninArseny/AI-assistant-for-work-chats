from sqlalchemy.ext.asyncio import AsyncSession
from command_service_app.repositories.message_repository import MessageRepository
from shared.schemas.TelegramApiDtos import TelegramMessage


class MessageService:
    def __init__(self, session: AsyncSession):
        self._messages = MessageRepository(session)

    async def get_user_messages(self, user_id: int):
        return await self._messages.get_user_messages(user_id)

    async def get_chat_messages(self, chat_id: int, limit: int):
        return await self._messages.get_chat_messages(chat_id, limit)

    async def get_chat_stats(self, chat_id: int):
        return await self._messages.get_chat_stats(chat_id)