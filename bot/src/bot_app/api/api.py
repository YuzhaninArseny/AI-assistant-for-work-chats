import asyncio
import logging

from aiogram.types import Message
from aiohttp import ClientSession

base_url = "http://saver:8000"


async def save_message(aios: ClientSession, message: Message):
    if message.forward_from is None:
        forward_from = None
    else:
        forward_from = {
            "id": message.forward_from.id,
            "username": message.forward_from.username
        }
    reply_to = None

    r = await aios.post(f"{base_url}/messages", json={
        "message_id": message.message_id,
        "from": {
            "id": message.from_user.id,
            "username": message.from_user.username
        },
        "chat": {
            "id": message.chat.id,
            "title": message.chat.title
        },
        "date": message.date.timestamp(),
        "text": message.text,
        "reply_to_message": reply_to,
        "forward_from": forward_from
    })

    if r.status != 201:
        logging.error(f"Couldn't save message")
        logging.error(r.text)


async def summarize(chat_id: int) -> str:
    await asyncio.sleep(5)
    return f"summarized text for chat {chat_id}"


async def search(char_id: int, query: str) -> str:
    await asyncio.sleep(3)
    return f"search result for '{query}' in chat {char_id}"


async def draft(chat_id: int) -> str:
    await asyncio.sleep(5)
    return f"draft text for chat {chat_id}"
