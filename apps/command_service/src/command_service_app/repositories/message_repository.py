from collections import defaultdict
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from shared.schemas.TelegramApiDtos import TelegramMessage, TelegramUser, TelegramChat, ChatStats, TopUser, \
    DailyUserActivity
from shared.models.messages import Message


# НАДО добавить общий Класс BaseRepo или абстрактный метод, который будет из таблицы table и по значению индекс_колонки
# index_column доставать list[TableORM]
class MessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

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
                id=db_message.chat_id,
            ),
            date=int(db_message.time_sent.timestamp()),
            **{
                "from": TelegramUser(
                    id=db_message.user_id,
                    username=db_message.username
                )
            },
            text=db_message.content
        ) for db_message in db_messages]
        return result_list

    async def get_chat_messages(self, chat_id: int, limit: int = 1400) -> list[TelegramMessage]:
        query = await self._session.scalars(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.time_sent.desc())
            .limit(limit)
        )
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
            date=int(db_message.time_sent.timestamp()),
            **{
                "from": TelegramUser(
                    id=db_message.user_id,
                    username=db_message.username
                )
            }
        ) for db_message in db_messages]
        return result_list

    async def get_chat_stats(self, chat_id: int) -> ChatStats:
        # Таймзона GMT+5
        tz_gmt5 = timezone(timedelta(hours=5))
        now_gmt5 = datetime.now(tz_gmt5)
        start_date_gmt5 = now_gmt5 - timedelta(days=14)

        start_utc_naive = start_date_gmt5.astimezone(timezone.utc).replace(tzinfo=None)

        # 1. Получаем все неслужебные сообщения за период
        stmt = select(Message.user_id, Message.time_sent).where(

                Message.chat_id == chat_id,
                Message.time_sent >= start_utc_naive,
                Message.is_service == False

        )

        result = await self._session.execute(stmt)
        rows = result.fetchall()

        # 2. Агрегируем данные в Python (надёжнее для работы с часовым поясом)
        top_counter: defaultdict[int, int] = defaultdict(int)
        daily_activity: defaultdict[str, defaultdict[int, int]] = defaultdict(lambda: defaultdict(int))

        for user_id, time_sent in rows:
            # time_sent — timezone-aware (UTC), если вы сохраняете его правильно
            if time_sent.tzinfo is None:
                # Если вдруг naive — интерпретируем как UTC
                time_sent = time_sent.replace(tzinfo=timezone.utc)

            # Переводим в GMT+5 и извлекаем дату
            local_time = time_sent.astimezone(tz_gmt5)
            day_key = local_time.strftime("%Y-%m-%d")

            top_counter[user_id] += 1
            daily_activity[day_key][user_id] += 1

        # 3. Формируем top_users (топ-5)
        top_users_sorted = sorted(top_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        top_users = [TopUser(user_id=uid, message_count=count) for uid, count in top_users_sorted]

        # 4. Гарантируем наличие всех 14 дней (включая пустые)
        all_days = [(start_date_gmt5 + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14)]
        full_daily_activity: dict[str, list[DailyUserActivity]] = {}
        for day in all_days:
            activities = [
                DailyUserActivity(user_id=uid, message_count=cnt)
                for uid, cnt in daily_activity.get(day, {}).items()
            ]
            full_daily_activity[day] = activities

        return ChatStats(
            top_users=top_users,
            daily_activity=full_daily_activity
        )

