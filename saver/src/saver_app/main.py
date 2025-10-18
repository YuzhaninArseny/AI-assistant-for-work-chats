from fastapi import FastAPI
import os
from saver_app.api.routes.messages import router as messages_router
from saver_app.api.routes.chats import router as chats_router
from saver_app.api.routes.users import router as users_router
from saver_app.core.errors.setup_logging import setup_logging
from saver_app.core.errors.handlers import register_error_handlers

setup_logging()
app = FastAPI()
register_error_handlers(app)
app.include_router(messages_router)
app.include_router(chats_router)
app.include_router(users_router)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "App is alive!"}
