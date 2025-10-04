from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("стартанули")


@router.message()
async def msg(message: Message):
    if message.chat.type in {"group", "supergroup"}:
        await message.answer(f"Сохраняем сообщение из {message.chat.id}: {message.text}")
    else:
        await message.answer(f": {message.text}")
