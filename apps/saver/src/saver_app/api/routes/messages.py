from logging import getLogger, INFO

from fastapi import APIRouter, status, Depends
from saver_app.services.message_service import MessageService
from shared.db.database import get_session
from shared.schemas.TelegramApiDtos import TelegramMessage
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/messages", tags=["messages"])

logger = getLogger("saver")
logger.setLevel(INFO)


@router.post("", response_model=TelegramMessage, status_code=status.HTTP_201_CREATED)
async def receive_message(message: TelegramMessage, session: AsyncSession = Depends(get_session)):
    logger.info(f"Saving message {message.message_id}")
    return await MessageService(session).add(message)
