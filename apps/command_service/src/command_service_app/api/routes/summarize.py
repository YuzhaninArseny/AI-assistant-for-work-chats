from logging import getLogger, INFO

from fastapi import APIRouter
from command_service_app.services.summarization.summarization_model import SummarizationModel
from command_service_app.repositories.db_client import DbClientDep

model = SummarizationModel()
router = APIRouter(prefix="/summarize", tags=["summarization"])
logger = getLogger("summarizer")
logger.setLevel(INFO)

@router.get("/")
def get_messages(dbclient: DbClientDep, chat_id: int, limit: int | None) -> str:
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
    summarize_text = model.summarize(prompt)
    logger.info(f"Summary for {chat_id} ready ({len(messages)} messages)")
    return summarize_text