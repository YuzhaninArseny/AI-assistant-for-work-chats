from sqlalchemy.ext.asyncio import AsyncSession

from saver_app.services.message_service import MessageService
from fastapi import APIRouter, status, Depends
from saver_app.schemas.tg_update import TelegramMessage
from saver_app.db.database import get_session
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/messages", response_model=list[TelegramMessage])
async def get_messages(user_id: int, session: AsyncSession = Depends(get_session)):
    return await MessageService(session).get_user_messages(user_id)