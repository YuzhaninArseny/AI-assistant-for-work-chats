from fastapi import APIRouter, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from shared.models.request_models import RelevantMessagesRequest, AddingMessagesRequest
from command_service_app.core.service_client import chroma_service_client

router = APIRouter(prefix="/relevant-messages", tags=["relevant-messages"])


@router.post('/')
async def get_relevant_messages(request: RelevantMessagesRequest, chat_id: Optional[str] = Query(None)):
    try:
        relevant_messages = await chroma_service_client.post('/relevant-messages', json={'key_words': request.key_words})
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


@router.post('/messages')
async def add_messages(request: AddingMessagesRequest):
    try:
        tg_messages_to_dicts = []
        for msg in request.messages:
            if msg.text is None:
                continue
            tg_messages_to_dicts.append(
                {
                    'text': msg['text'],
                    'message_id': str(msg.message_id),
                    'chat_id': str(msg.chat.id),
                    'timestamp': msg.date
                }
            )

        await chroma_service_client.post('/messages', json={'messages': tg_messages_to_dicts})

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
