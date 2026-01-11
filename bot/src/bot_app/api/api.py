import logging

from aiogram.types import Message
from aiohttp import ClientSession

base_url = "http://saver:8000"
command_base_url = "http://command_app:8001"


async def save_message(aios: ClientSession, message: Message):
    if message.forward_from is None:
        forward_from = None
    else:
        forward_from = {
            "id": message.forward_from.id,
            "username": message.forward_from.username
        }
    reply_to = None
    try:
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
    except Exception as e:
        logging.error(f"Error saving message for chat {message.chat.id}: {e}")
        return

    if r.status != 201:
        logging.error(f"Couldn't save message")
        logging.error(r.text)


async def summarize(aios: ClientSession, chat_id: int) -> str:
    try:
        resp = await aios.get(f"{command_base_url}/summarize/", params={"chat_id": chat_id})
    except Exception as e:
        logging.error(f"Error summarizing chat {chat_id}: {e}")
        return "Произошла ошибка"

    if resp.status != 200:
        return "Произошла ошибка"
    return str(await resp.json())


async def search(aios: ClientSession, chat_id: int, query: list[str]) -> str:
    try:
        resp = await aios.post(f"{command_base_url}/relevant-messages/", params={"chat_id": chat_id},
                               json={"key_words": query})
    except Exception as e:
        logging.error(f"Error searching in chat {chat_id}: {e}")
        return "Произошла ошибка"
    if resp.status != 200:
        return "Произошла ошибка"
    return str(await resp.json())


async def draft(aios: ClientSession, chat_id: int) -> str:
    try:
        resp = await aios.post(f"{command_base_url}/draft/", params={"chat_id": chat_id}, )
    except Exception as e:
        logging.error(f"Error searching in chat {chat_id}: {e}")
        return "Произошла ошибка"
    if resp.status != 200:
        return "Произошла ошибка"
    return str(await resp.json())
