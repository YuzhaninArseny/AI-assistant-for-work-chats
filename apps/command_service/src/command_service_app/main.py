from fastapi import FastAPI

from command_service_app.api.routes.chats import router as chats_router
from command_service_app.api.routes.draft import router as draft_router
from command_service_app.api.routes.groups import router as groups_router
from command_service_app.api.routes.relevant_messages import router as relevant_messages_router
from command_service_app.api.routes.summarize import router as summarize_router
from command_service_app.api.routes.users import router as users_router
from command_service_app.repositories.db_client import load_db_lifespan

app = FastAPI(lifespan=load_db_lifespan)

app.include_router(chats_router)
app.include_router(groups_router)
app.include_router(draft_router)
app.include_router(users_router)
app.include_router(relevant_messages_router)
app.include_router(summarize_router)


@app.get("/ping")
def read_root():
    return {"status": "ok", "message": "App is alive!"}
