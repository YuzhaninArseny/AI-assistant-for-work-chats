import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


def draft_filter(message: Message):
    r = re.search(r"/draft ([\w\s]+)", message.text)
    if r:
        return {"group": r.group(1)}


@router.message(Command(commands="draft"), draft_filter)
async def draft(message: Message, group: str, ):
    await message.answer(f"draft for {group}")
