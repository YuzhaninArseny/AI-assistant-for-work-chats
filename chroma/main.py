from fastapi import FastAPI
from typing import List

# в метаинфе буду хранить ссылки на сообщения в чатах, chat_id

app = FastAPI()

@app.get('/get-relevant-messages')
def get_relevant_messages(key_words: List[str]):
    pass