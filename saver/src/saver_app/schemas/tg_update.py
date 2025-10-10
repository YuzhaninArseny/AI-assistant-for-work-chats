from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from examples import TELEGRAM_MESSAGE_EXAMPLE


class TelegramUpdate(BaseModel):
    """
    TelegramUpdate — объект, который Telegram присылает боту при каждом событии (update).

    Содержит метаданные обновления (update_id) и один из возможных типов данных:
    сообщение, callback, команду и т.п.
    В данном случае рассматриваем только события с сообщениями (`message`).

    **Поля:**
    - **update_id (int)** — уникальный идентификатор обновления,
      используется для определения порядка событий.
      *Обязательное поле.*
    - **message (TelegramMessage | None)** — объект сообщения, если обновление содержит сообщение.
      *Необязательное поле.*
    """

    update_id: int
    message: Optional[TelegramMessage] = None


class TelegramMessage(BaseModel):
    """
    TelegramMessage — объект сообщения, отправленного пользователем или сервисом.

    Соответствует полю `message` внутри Telegram Update.

    **Поля:**
    - **message_id (int)** — уникальный идентификатор сообщения в пределах чата.
      *Обязательное поле.*

    - **from_ (TelegramUser | None)** — объект пользователя, отправившего сообщение.
      Может отсутствовать у сервисных сообщений.
      *Необязательное поле.*

    - **chat (TelegramChat)** — объект чата, в котором отправлено сообщение.
      *Обязательное поле.*

    - **date (int)** — время отправки сообщения в виде UNIX-timestamp (секунды).
      Может быть преобразовано в `datetime` через `datetime.fromtimestamp(date)`.
      *Обязательное поле.*

    - **text (str | None)** — текст сообщения, если оно текстовое.
      *Необязательное поле.*

    - **reply_to_message (TelegramMessage | None)** — ссылка на сообщение, на которое был дан ответ.
      *Необязательное поле.*

    - **forward_from (TelegramUser | None)** — объект пользователя, от которого сообщение было переслано.
      *Необязательное поле.*
    """
    model_config = ConfigDict(populate_by_name=True, json_schema_extra={"example": TELEGRAM_MESSAGE_EXAMPLE})
    message_id: int
    from_: Optional[TelegramUser] = Field(None, alias="from")
    chat: TelegramChat
    date: int
    text: Optional[str] = None

    reply_to_message: Optional[TelegramMessage] = None
    forward_from: Optional[TelegramUser] = None


class TelegramUser(BaseModel):
    """
    TelegramUser — объект пользователя Telegram.

    Содержит базовую информацию о пользователе, если она предоставлена Telegram API.

    **Поля:**
    - **id (int)** — уникальный идентификатор пользователя Telegram.
      Используется как `user_id` в БД.
      *Обязательное поле.*

    - **username (str | None)** — имя пользователя (без @).
      Может быть отсутствующим у пользователей без юзернейма.
      *Необязательное поле.*
    """

    id: int = Field(..., description="ID пользователя (user_id)")
    username: Optional[str] = None


class TelegramChat(BaseModel):
    """
    TelegramChat — объект, описывающий чат, из которого пришло сообщение.

    Может представлять как личный диалог, так и группу, супергруппу или канал.

    **Поля:**
    - **id (int)** — уникальный идентификатор чата (`chat_id`).
      *Обязательное поле.*

    - **title (str | None)** — название чата (группы, канала).
      Отсутствует у личных диалогов.
      *Необязательное поле.*
    """

    id: int = Field(..., description="ID чата (chat_id)")
    title: Optional[str] = None
