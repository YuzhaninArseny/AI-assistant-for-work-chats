import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from command_service_app.core.service_client import summarization_client, ServiceClient
from command_service_app.repositories.db_client import DbClientDep

router = APIRouter(prefix="/summarize", tags=["summarization"])

# Настраиваем логгер с обработчиком для гарантии вывода в stdout
logger = logging.getLogger("summarizer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_summarization_model():
    return summarization_client


SummarizationModelDep = Annotated[ServiceClient, Depends(get_summarization_model)]


@router.get("/")
async def get_messages(
        dbclient: DbClientDep,
        model_client: SummarizationModelDep,
        chat_id: int,
        limit: int | None = None
) -> str:
    messages = dbclient.get_chat_messages(chat_id, limit)

    if len(messages) == 0:
        logger.info(f"No messages to summarize in chat {chat_id}")
        return "В чате нет активности"

    # Фильтруем сообщения с непустым content и сохраняем объекты (нужен username)
    filtered_messages = [
        msg for msg in messages
        if msg.content is not None and msg.content.strip()
    ]

    if not filtered_messages:
        logger.info(f"No valid text messages in chat {chat_id} (only service/empty messages)")
        return "В чате нет сообщений с текстом для суммаризации"

    # Разворачиваем список: от старых сообщений к новым (хронологический порядок)
    filtered_messages.reverse()

    # Формируем диалог: {username}: {content}
    dialog_lines = []
    for i, msg in enumerate(filtered_messages, 1):
        author = msg.username or "user"
        content = msg.content.strip()
        # Опционально: обрезаем слишком длинные сообщения
        if len(content) > 150:
            content = content[:150] + "..."
        dialog_lines.append(f"{i}. {author}: {content}")

    dialog_text = "\n".join(dialog_lines)

    prompt = f"""
Суммаризируй следующий Telegram-чат, выделив:

1. Основные темы обсуждения
2. Ключевые решения
3. Важные моменты
4. Нерешённые вопросы
5. Общий тон

Чат:
{dialog_text}
"""

    # Логируем полный промпт
    logger.info(f"Full prompt sent to model:\n{prompt}")

    try:
        response = await model_client.post("/summarize", json={"prompt": prompt})
        logger.info(f"Summary for chat {chat_id} ready ({len(filtered_messages)} messages used)")
        return response
    except Exception as e:
        logger.error(f"Failed to summarize chat {chat_id}: {e}")
        return "Не удалось сгенерировать суммаризацию. Попробуйте позже."