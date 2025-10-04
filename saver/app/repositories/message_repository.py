from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.config import settings
from datetime import datetime
from app.schemas.tg_update import TelegramMessage, TelegramUser, TelegramChat
from app.models.messages import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, message: TelegramMessage) -> TelegramMessage:
        db_message = Message(
            message_id=message.message_id,
            user_id=message.from_.id if message.from_ else None,
            chat_id=message.chat.id,
            content=message.text,
            time_sent=datetime.fromtimestamp(message.date),
        )

        self._session.add(db_message)
        await self._session.commit()
        await self._session.refresh(db_message)
        return TelegramMessage(
            message_id=db_message.message_id,
            chat=TelegramChat(id=db_message.chat_id),
            date=int(db_message.time_sent.timestamp()),
            **{
                "from": TelegramUser(
                    id=db_message.user_id,
                    username="mocked"
                )
            }
        )
