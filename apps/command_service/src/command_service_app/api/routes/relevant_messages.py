import traceback
from logging import getLogger, INFO
from typing import Optional, Annotated, List

from fastapi import APIRouter, status, Query, Depends
from fastapi.responses import JSONResponse

from command_service_app.core.service_client import chroma_service_client, ServiceClient
from shared.models.request_models import RelevantMessagesRequest, AddingMessagesRequest
from shared.schemas.TelegramApiDtos import TelegramMessage
from command_service_app.core.service_client import chroma_service_client

router = APIRouter(prefix="/relevant-messages", tags=["relevant-messages"])

logger = getLogger("relevant-messages")
logger.setLevel(INFO)


def get_chroma_client():
    return chroma_service_client


ChromaClientDep = Annotated[ServiceClient, Depends(get_chroma_client)]


@router.post('/')
async def get_relevant_messages(request: RelevantMessagesRequest, chroma_client: ChromaClientDep,
                                chat_id: Optional[str] = Query(None)):
    try:
        relevant_messages = await chroma_client.post('/relevant-messages', json={'key_words': request.key_words})
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
        logger.error(traceback.format_exc())
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
async def add_messages(messages: List[TelegramMessage], chroma_client: ChromaClientDep):
    try:
        tg_messages_to_dicts = []
        for msg in messages:
            if msg.text is None:
                continue
            tg_messages_to_dicts.append(
                {
                    'text': msg.text,
                    'message_id': str(msg.message_id),
                    'chat_id': str(msg.chat.id),
                    'timestamp': msg.date
                }
            )

        await chroma_client.post('/messages', json={'messages': tg_messages_to_dicts})

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "added_messages": len(messages)
            }
        )
    except Exception as e:
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Внутренняя ошибка сервера",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": repr(e),
            }
        )
