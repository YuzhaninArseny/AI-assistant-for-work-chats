from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.database import get_session
from shared.models.messages import Message
from shared.schemas.TelegramApiDtos import TelegramMessage, TelegramUser, TelegramChat


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
            chat_title=message.chat.title
        )

        self._session.add(db_message)
        await self._session.commit()
        await self._session.refresh(db_message)
        return TelegramMessage(
            message_id=db_message.message_id,
            chat=TelegramChat(id=db_message.chat_id,
                              title=db_message.chat_title),
            date=int(db_message.time_sent.timestamp()),
            text=db_message.content,
            from_ = TelegramUser(
                    id=db_message.user_id,
                    username=db_message.username
                )
        ).model_dump()


def __get_repo(session: Annotated[AsyncSession, Depends(get_session)]):
    return MessageRepository(session)


MessagesRepoDep = Annotated[MessageRepository, Depends(__get_repo)]
