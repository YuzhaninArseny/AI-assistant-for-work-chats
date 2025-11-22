from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from command_service_app.repositories.db_client import DbClientDep
from command_service_app.services.response_draft_generator.draft_model import ResponseDraftGenerator

model = ResponseDraftGenerator()
router = APIRouter(prefix="/summarize", tags=["summarization"])


@router.get('/')
def draft(db_client: DbClientDep, chat_id: int):
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
                    'content': msg['text'],
                    'message_id': str(msg.message_id),
                    'chat_id': str(msg.chat.id),
                    'timestamp': msg.date
                }
            )

        draft = model.generate(tg_messages_to_dicts)
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
                "details": str(e),
            }
        )
