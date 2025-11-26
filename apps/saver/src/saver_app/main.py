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


def get_chroma_client():
    return httpx.AsyncClient(base_url="http://chroma:8082")


ChromaClientDep = Annotated[httpx:AsyncClient, Depends(get_chroma_client)]


@app.post("/messages", response_model=TelegramMessage, status_code=status.HTTP_201_CREATED)
async def receive_message(message: TelegramMessage, repo: MessagesRepoDep, chroma: ChromaClientDep):
    logger.info(f"Saving message {message.message_id}")
    message_ = await repo.add(message)
    print("BIBA")

    await chroma.post("/messages", json={"messages": [message.model_dump()]})
    return message_


@app.get("/ping")
def read_root():
    return {"status": "ok", "message": "App is alive!"}
