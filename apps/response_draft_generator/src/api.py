from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import List, Dict
from draft_model import ResponseDraftGenerator

model = ResponseDraftGenerator()
router = APIRouter(prefix="/summarize", tags=["summarization"])


@router.get('/')
def draft(messages: List[Dict]):
    try:
        draft = model.generate(messages)
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
