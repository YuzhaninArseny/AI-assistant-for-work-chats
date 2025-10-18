from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from saver_app.core.config import settings
from saver_app.schemas.TelegramApiDtos import TelegramUpdate


class UpdateRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    def add(self, update: TelegramUpdate):
        pass
