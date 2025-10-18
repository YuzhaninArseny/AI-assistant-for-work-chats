from http import HTTPStatus

from fastapi import APIRouter, status
from saver_app.schemas.TelegramApiDtos import TelegramUpdate

router = APIRouter(prefix="/updates", tags=["updates"])


@router.post("", response_model=TelegramUpdate, status_code=status.HTTP_201_CREATED)
async def receive_update(update: TelegramUpdate):
    pass