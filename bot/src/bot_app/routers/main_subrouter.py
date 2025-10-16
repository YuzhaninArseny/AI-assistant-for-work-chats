from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiohttp import ClientSession

from bot_app.api.api import save_message
router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("стартанули")


@router.message()
async def msg(message: Message, aiohttp_session: ClientSession):
    if message.chat.type in {"group", "supergroup"}:
        await save_message(aiohttp_session, message)
    else:
        await message.answer(f": {message.text}")
