from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.config import settings
from app.repositories.update_repository import UpdateRepository

class UpdateService:
    def __init__(self, session: AsyncSession):
        self._messages = UpdateRepository(session)