from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import ScalarResult
from typing import Any, Optional
from fastapi import HTTPException, status
from saver_app.core.config import settings
from datetime import datetime
from saver_app.schemas.TelegramApiDtos import TelegramMessage, TelegramUser, TelegramChat
from saver_app.models.messages import Message

# НАДО добавить общий Класс BaseRepo или абстрактный метод, который будет из таблицы table и по значению индекс_колонки
# index_column доставать list[TableORM]
class MessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, message: TelegramMessage) -> TelegramMessage:
        db_message = Message(
            message_id=message.message_id,
            user_id=message.from_.id,
            chat_id=message.chat.id,
            content=message.text,
            username=message.from_.username,
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
                    username=db_message.username
                )
            }
        )

    async def get_user_messages(self, user_id: int) -> list[TelegramMessage]:
        query = await self._session.scalars(select(Message).where(Message.user_id == user_id))
        db_messages = query.all()
        if not db_messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            )
        result_list = [TelegramMessage(
            message_id=db_message.message_id,
            chat=TelegramChat(
                id = db_message.chat_id,
            ),
            date=db_message.time_sent.timestamp(),
            **{
                "from": TelegramUser(
                    id=db_message.user_id,
                    username=db_message.username
                )
            },
            text=db_message.content
        ) for db_message in db_messages]
        return result_list

    async def get_chat_messages(self, chat_id: int) -> list[TelegramMessage]:
        query = await self._session.scalars(select(Message).where(Message.chat_id == chat_id))
        db_messages = query.all()
        if not db_messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            )
        result_list = [TelegramMessage(
            message_id=db_message.message_id,
            chat=TelegramChat(
                id=db_message.chat_id,
            ),
            date=db_message.time_sent.timestamp(),
            **{
                "from": TelegramUser(
                    id=db_message.user_id,
                    username=db_message.username
                )
            }
        ) for db_message in db_messages]
        return result_list

