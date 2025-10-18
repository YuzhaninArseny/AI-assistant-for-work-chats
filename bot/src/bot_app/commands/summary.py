import re
import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router= Router()
summary_service_url = "http://summarization:1234/summarize"


def summary_filter(message: Message):
    r = re.search(r"/summary ([\w_]+)", message.text)
    if r:
        return {"group": r.group(1)}


@router.message(Command(commands="summary"), summary_filter)
async def summary(message: Message, group: str):
    params = {
        "chat_id": group,
        "limit": None
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(summary_service_url, params=params) as resp:
                if resp.status == 200:
                    summary_text = await resp.text()
                else:
                    summary_text = f"Ошибка: сервис суммаризации вернул статус {resp.status}"
    except Exception as e:
        summary_text = f"Не удалось получить ответ от сервиса суммаризации: {e}"

    await message.reply(summary_text)
