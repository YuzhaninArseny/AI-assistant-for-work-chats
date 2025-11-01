from fastapi import FastAPI
import os
from saver_app.api.routes.messages import router as messages_router
app = FastAPI()

app.include_router(messages_router)
@app.get("/ping")
def read_root():
    return {"status": "ok", "message": "App is alive!"}

