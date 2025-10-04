from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.tg_update import TelegramUpdate


class UpdateRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    def add(self, update: TelegramUpdate):
        pass
