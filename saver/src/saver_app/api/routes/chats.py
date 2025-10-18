from sqlalchemy.ext.asyncio import AsyncSession

from saver_app.services.message_service import MessageService
from fastapi import APIRouter, status, Depends
from saver_app.schemas.TelegramApiDtos import TelegramMessage
from saver_app.db.database import get_session
router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/{chat_id}/messages", response_model=list[TelegramMessage])
async def get_messages(chat_id: int, session: AsyncSession = Depends(get_session)):
    return await MessageService(session).get_chat_messages(chat_id)