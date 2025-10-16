import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


def search_filter(message: Message):
    r = re.search(r"/search ([\w_]+) ([\w\s]+)", message.text)
    if r:
        return {"group": r.group(1), "query": r.group(2)}


@router.message(Command(commands="search"), search_filter)
async def search(message: Message, group: str, query: str):
    await message.answer(f"search in {group} for {query}")
