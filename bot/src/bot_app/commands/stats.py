import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router= Router()


def stats_filter(message: Message):
    r = re.search(r"/stats ([\w\s]+)", message.text)
    if r:
        return {"group": r.group(1)}


@router.message(Command(commands="stats"), stats_filter)
async def stats(message: Message, group: str, ):
    await message.answer(f"stats for {group}")
