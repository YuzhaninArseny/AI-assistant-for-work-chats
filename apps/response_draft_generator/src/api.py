from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from draft_model import ResponseDraftGenerator
from request_models import ResponseDraftGeneratorRequest


model = ResponseDraftGenerator()
router = APIRouter(prefix="/draft", tags=["draft"])


@router.post('/')
def draft(request: ResponseDraftGeneratorRequest):
    try:
        draft = model.generate(request.messages)
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
