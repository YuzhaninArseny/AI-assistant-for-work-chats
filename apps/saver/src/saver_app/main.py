from logging import getLogger, INFO

from fastapi import FastAPI, status

from saver_app.message_repository import MessagesRepoDep
from shared.schemas.TelegramApiDtos import TelegramMessage

logger = getLogger("saver")
logger.setLevel(INFO)
app = FastAPI()


@app.post("/messages", response_model=TelegramMessage, status_code=status.HTTP_201_CREATED)
async def receive_message(message: TelegramMessage, repo: MessagesRepoDep):
    logger.info(f"Saving message {message.message_id}")
    return await repo.add(message)


@app.get("/ping")
def read_root():
    return {"status": "ok", "message": "App is alive!"}
