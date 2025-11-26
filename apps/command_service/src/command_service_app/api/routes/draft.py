from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from command_service_app.core.service_client import response_draft_generator_client, ServiceClient
from command_service_app.repositories.db_client import DbClientDep

router = APIRouter(prefix="/draft", tags=["draft"])


def get_draft_client():
    return response_draft_generator_client


DraftGeneratorClientDep = Annotated[ServiceClient, Depends(get_draft_client)]


@router.get('/')
async def draft(db_client: DbClientDep, chat_id: int, draft_client: DraftGeneratorClientDep):
    try:
        messages = db_client.get_chat_messages(chat_id)
        if len(messages) == 0:
            return 'Невозможно составить черновик ответа - вопросов не обнаружено'

        tg_messages_to_dicts = []
        for msg in messages:
            if msg.text is None:
                continue
            tg_messages_to_dicts.append(
                {
                    'content': msg.text,
                    'message_id': str(msg.message_id),
                    'chat_id': str(msg.chat.id),
                    'timestamp': msg.date
                }
            )

        draft = await draft_client.post('/draft', json={'messages': messages})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=draft
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
