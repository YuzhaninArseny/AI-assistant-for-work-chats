import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router= Router()


def summary_filter(message: Message):
    r = re.search(r"/summary ([\w_]+)", message.text)
    if r:
        return {"group": r.group(1)}


@router.message(Command(commands="summary"), summary_filter)
async def summary(message: Message, group: str):
    await message.answer(f"Summary for {group}")
