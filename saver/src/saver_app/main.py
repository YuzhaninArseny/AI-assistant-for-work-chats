from fastapi import FastAPI
import os
from saver_app.api.routes.messages import router as messages_router
from saver_app.api.routes.chats import router as chats_router
from saver_app.api.routes.users import router as users_router
app = FastAPI()

app.include_router(messages_router)
app.include_router(chats_router)
app.include_router(users_router)
@app.get("/")
def read_root():
    return {"status": "ok", "message": "App is alive!"}

@app.get("/env")
def read_env():
    return {
        "app_name": os.getenv("APP_NAME", "undefined"),
        "env": os.getenv("APP_ENV", "dev"),
        "host": os.getenv("APP_HOST", "0.0.0.0"),
        "port": os.getenv("APP_PORT", "8000"),
    }
