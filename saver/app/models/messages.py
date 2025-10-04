from __future__ import annotations
from datetime import datetime
from typing import Optional, Any, Dict

from sqlalchemy import (
    BigInteger, DateTime, String, Text, UniqueConstraint,
    Index, func, event, DDL, Boolean
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, Field
from app.models.base import Base

class Message(Base):
    """
    Таблица `messages` — хранит сообщения, поступающие от Telegram-бота.

    Каждая запись соответствует одному сообщению из чата Telegram.
    В таблице предусмотрены индексы для полнотекстового поиска и поиска с опечатками.

    **Описание полей:**

    - **id (int)** — первичный ключ, автоинкремент, уникальный идентификатор записи в таблице.
      *Обязательное поле.*

    - **user_id (int)** — идентификатор пользователя Telegram, который отправил сообщение.
      Соответствует `from.id` в Telegram API.
      *Обязательное поле.*

    - **chat_id (int)** — идентификатор чата, в котором было отправлено сообщение.
      Соответствует `chat.id` в Telegram API.
      *Обязательное поле.*

    - **message_id (int)** — идентификатор самого сообщения в рамках данного чата.
      В паре `(chat_id, message_id)` должен быть уникален.
      *Обязательное поле.*

    - **content (str | None)** — текстовое содержимое сообщения.
      Может быть `NULL`, если сообщение служебное (например, «пользователь вступил в группу»).
      *Необязательное поле.*

    - **is_service (bool)** — флаг, показывающий, является ли сообщение служебным
      (например, уведомление о присоединении к чату, закреплении сообщения и т.п.).
      *Обязательное поле, по умолчанию False.*

    - **reply_to_message_id (int | None)** — идентификатор сообщения, на которое данное сообщение является ответом.
      Используется для восстановления древовидной структуры диалогов.
      *Необязательное поле.*

    - **forward_from_user_id (int | None)** — идентификатор пользователя, от которого было переслано сообщение.
      *Необязательное поле.*

    - **time_sent (datetime)** — время отправки сообщения (из Telegram API `date`).
      Хранится в формате `DateTime(timezone=True)`.
      *Обязательное поле.*

    - **time_loaded (datetime)** — время загрузки сообщения в базу.
      Автоматически выставляется функцией `now()` на сервере.
      *Обязательное поле, по умолчанию текущее время.*

    - **tsv (str | None)** — поле для полнотекстового поиска (PostgreSQL TSVECTOR).
      Заполняется при индексировании содержимого.
      *Необязательное служебное поле.*
    """

    __tablename__ = "messages"

    __table_args__ = (
        # Уникальность сообщения в пределах чата
        UniqueConstraint('chat_id', 'message_id', name='uq_chat_msg'),

        # Индекс для полнотекстового поиска по TSVECTOR
        Index("ix_messages_tsv", "tsv", postgresql_using="gin"),

        # Триграммный индекс для поиска по опечаткам (ILIKE)
        Index(
            "ix_messages_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"}
        ),

        # Индекс для сортировки сообщений по времени внутри чата
        Index("ix_messages_chat_time", "chat_id", "time_sent"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, index=True)

    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_service: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reply_to_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)
    forward_from_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)

    time_sent: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    time_loaded: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    tsv: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

