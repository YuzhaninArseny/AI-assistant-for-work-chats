from fastapi import FastAPI
from summarization_model import SummarizationModel
from db_client import load_db_lifespan, DbClientDep

model = SummarizationModel()
app = FastAPI(lifespan=load_db_lifespan)


@app.get("/summarize")
def get_messages(dbclient: DbClientDep, chat_id: int, limit: int | None) -> str:
    messages = dbclient.get_chat_messages(chat_id, limit)
    if len(messages) == 0:
        return 'В чате нет активности'

    # уточнить у эксперта, как сделать этот промпт лучше
    text = " ".join([msg.content for msg in messages])
    summarize_text = model.summarize(text)

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