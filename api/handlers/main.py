from typing import List
from fastapi import FastAPI

# Это все дело будет выполняться на сервере aiogram

app = FastAPI()

@app.get('/summary')
def summary(user_id, chat_id):
    # 1) Обращаемся к БД значитс и получаем по названию чата все сообщения за последние 24 ч
    # 2) Нужно создать промпт
    # 3) Отправить промпт в ллм, получить ответ и собрать его в адекватный
    # 4) Отправить ответ пользователю

    messages: List[str] = db_client.get_messages(user_id, chat_id)

    # отправляем запрос в сервис суммаризации

    # получаем ответ и отправляем обратно пользователю


@app.get('/search')
def search(user_id, chat_id, key_words: List[str]):

    relevant_messages: List[str] = chroma_client.get_relevant_messages()

    # опционально: приведение сообщений к репрезентативному виду


@app.get('/stats')
def stats(user_id, chat_id):
    # 1) Активность по дням: т.е. нужен графичек или просто текст (тут уточнить),
    # где по ОХ - имена пользователей, по OY - количество отправленных ими сообщений
    # 2) Топ-5 активных участников (уточнить, за какой промежуток времени?)
    pass


@app.get('/draft')
def draft(user_id, chat_id):
    # Вопрос: в ТЗ сказано, что "бот анализирует последние сообщения в цепочке"
    # Последние - это какие? Сколько?

    # Отправляем запросы в ту же модель суммаризации
    messages: List[str] = db_client.get_messages(user_id, chat_id)

    # здесь можно отдать власть Димуле, чтобы он составил хороший промпт
    prompt = f""" 
            сообщения:
                {" ".join(messages)}
        """

