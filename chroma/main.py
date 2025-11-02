from fastapi import FastAPI, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from search_engine import ChromaChatSearchEngine
from shemas.DTO import TelegramMessage

engine = ChromaChatSearchEngine()
app = FastAPI()


@app.get('/relevant-messages')
def get_relevant_messages(key_words: List[str] = Query(...), chat_id: Optional[str] = Query(None)):
    try:
        relevant_messages = engine.search(key_words)
        if chat_id is not None:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={f'{chat_id}': relevant_messages.get(chat_id)}
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=relevant_messages
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Внутренняя ошибка сервера",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e),
            }
        )



# Для окончательного формирования ответа остается только в методе бота собрать из сообщений
# md-ответ и все
@app.post('/messages')
def add_messages(messages: List[TelegramMessage]):
    try:
        engine.add_chat_messages(messages)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "added_messages": len(messages)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Внутренняя ошибка сервера",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e),
            }
        )
