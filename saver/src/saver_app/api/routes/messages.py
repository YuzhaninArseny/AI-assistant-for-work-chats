from sqlalchemy.ext.asyncio import AsyncSession

from saver_app.services.message_service import MessageService
from fastapi import APIRouter, status, Depends
from saver_app.schemas.tg_update import TelegramMessage
from saver_app.db.database import get_session
router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=TelegramMessage, status_code=status.HTTP_201_CREATED)
async def receive_message(message: TelegramMessage, session: AsyncSession = Depends(get_session)):
    return await MessageService(session).add(message)