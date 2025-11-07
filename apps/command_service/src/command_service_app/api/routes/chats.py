from logging import getLogger, INFO

from sqlalchemy.ext.asyncio import AsyncSession
from command_service_app.services.message_service import MessageService
from fastapi import APIRouter, Depends
from shared.schemas.TelegramApiDtos import TelegramMessage
from shared.db.database import get_session
router = APIRouter(prefix="/chats", tags=["chats"])

logger = getLogger("command")
logger.setLevel(INFO)

@router.get("/{chat_id}/messages", response_model=list[TelegramMessage])
async def get_messages(chat_id: int, session: AsyncSession = Depends(get_session)):
    logger.info(f"Reading chat messages: {chat_id}")
    return await MessageService(session).get_chat_messages(chat_id)