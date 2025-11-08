from fastapi import APIRouter
from command_service_app.services.summarization.summarization_model import SummarizationModel
from command_service_app.repositories.db_client import DbClientDep

model = SummarizationModel()
router = APIRouter(prefix="/summarize", tags=["summarization"])

@router.get("/")
def get_messages(dbclient: DbClientDep, chat_id: int, limit: int | None) -> str:
    messages = dbclient.get_chat_messages(chat_id, limit)
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

    return summarize_text


#  Какими свойствами должна обладать функция draft, предназначенная для
# создания черновика ответа на полученные сообщения:
# 1) Понимание контекста и сути: Что обсуждается? Какая основная мысль или вопрос
#    затрагивается?
# 2) Намерение (Intent Recognition): Чего хочет от вас собеседник? 
# Запрос информации, подтверждение, выражение благодарности, жалоба? 
# От этого зависит тип ответа.
# 3) Учет истории диалога: какие предыдущие сообщения уже были обсуждены? Какие
#    аргументы уже поднимались?
# 4) Обработка опечаток и грамматических ошибок: как правильно формулировать
#    ответы, учитывая специфику русского языка?
# 5) Ключевые сущности: Имена, даты, проекты, продукты — бот должен корректно их использовать в черновике.
#
#
def draft():
    pass