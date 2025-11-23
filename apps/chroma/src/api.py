from typing import List, Optional, Dict
from fastapi import FastAPI, status, Query
from fastapi.responses import JSONResponse
from search_engine import ChromaChatSearchEngine
from request_models import RelevantMessagesRequest, AddingMessagesRequest


engine = ChromaChatSearchEngine()
app = FastAPI()


@app.post('/relevant-messages')
def get_relevant_messages(request: RelevantMessagesRequest, chat_id: Optional[str] = Query(None)):
    try:
        relevant_messages = engine.search(request.key_words)
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
                "details": repr(e),
            }
        )


@app.post('/messages')
def add_messages(request: AddingMessagesRequest):
    try:
        engine.add_chat_messages(request.messages)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "added_messages": len(request.messages)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Внутренняя ошибка сервера",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": repr(e),
            }
        )