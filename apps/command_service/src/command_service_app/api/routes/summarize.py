from logging import getLogger, INFO
from typing import Annotated

from fastapi import APIRouter, Depends

from command_service_app.core.service_client import summarization_client, ServiceClient
from command_service_app.repositories.db_client import DbClientDep

router = APIRouter(prefix="/summarize", tags=["summarization"])
logger = getLogger("summarizer")
logger.setLevel(INFO)


def get_summarization_model():
    return summarization_client


SummarizationModelDep = Annotated[ServiceClient, Depends(get_summarization_model)]


@router.get("/")
async def get_messages(dbclient: DbClientDep, model_client: SummarizationModelDep,
                       chat_id: int, limit: int | None = None) -> str:
    messages = dbclient.get_chat_messages(chat_id, limit)
    logger.info(
        f"Summarizing chat {chat_id} from {messages[0].message_id} to {messages[-1].message_id} ({len(messages)} messages)")
    if len(messages) == 0:
        return 'В чате нет активности'

    prompt = f"""
        Суммаризируй следующие Telegram сообщения, выделив:

            1. **Основные темы обсуждения** - какие вопросы поднимались
            2. **Ключевые решения** - что было решено
            3. **Важные моменты** - значимые идеи или информация
            4. **Вопросы, требующие внимания** - что осталось нерешенным
            5. **Общий тон дискуссии** - настроение участников
        
        Сообщения:
            {" ".join([msg.content for msg in messages])}
    """
    summarize_text = await model_client.post("/summarize", json={"prompt": prompt})
    logger.info(f"Summary for {chat_id} ready ({len(messages)} messages)")
    return summarize_text
