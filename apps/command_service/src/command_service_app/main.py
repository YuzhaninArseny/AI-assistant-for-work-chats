from fastapi import FastAPI
from command_service_app.api.routes.chats import router as chats_router
from command_service_app.api.routes.users import router as users_router
app = FastAPI()

app.include_router(chats_router)
app.include_router(users_router)
@app.get("/ping")
def read_root():
    return {"status": "ok", "message": "App is alive!"}

