from sqlalchemy.ext.asyncio import AsyncSession
from apps.shared.schemas import TelegramUpdate


class UpdateRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    def add(self, update: TelegramUpdate):
        pass
