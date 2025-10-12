from fastapi import FastAPI

from db_client import load_db_lifespan, DbClientDep

app = FastAPI(lifespan=load_db_lifespan)


@app.get("/test")
def get_messages(dbclient: DbClientDep, chat_id: int, limit: int | None):
    return dbclient.get_chat_messages(chat_id, limit)
