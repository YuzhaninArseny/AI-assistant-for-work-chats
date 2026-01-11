import os
from logging import getLogger, INFO
from typing import Annotated

import httpx
from fastapi import FastAPI, status, Depends
from httpx import AsyncClient

from saver_app.message_repository import MessagesRepoDep
from shared.schemas.TelegramApiDtos import TelegramMessage

logger = getLogger("saver")
logger.setLevel(INFO)
app = FastAPI()
CHROMA_HOST = os.getenv("CHROMA_HOST") or "chroma:8082"


def get_chroma_client():
    return httpx.AsyncClient(base_url=f"http://{CHROMA_HOST}")


ChromaClientDep = Annotated[httpx.AsyncClient, Depends(get_chroma_client)]


@app.post("/messages", response_model=TelegramMessage, status_code=status.HTTP_201_CREATED)
async def receive_message(message: TelegramMessage, repo: MessagesRepoDep, chroma: ChromaClientDep):
    logger.info(f"Saving message {message.message_id}")
    message_ = await repo.add(message)
    messages = [
        {
            'message_id': message.message_id,
            'chat_id': message.chat.id,
            'timestamp': message.date,
            'text': message.text
        }
    ]
    resp = await chroma.post("/messages", json={"messages": messages})
    if resp.status_code == 500:
        logger.error(f"Error sending to chroma: {resp.json()['details']}")
    return message_


@app.get("/ping")
def read_root():
    return {"status": "ok", "message": "App is alive!"}
