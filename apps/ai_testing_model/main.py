from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class RelevantMessagesRequest(BaseModel):
    key_words: list[str]


class AddingMessagesRequest(BaseModel):
    messages: list[dict]


@app.post("/relevant-messages")
def get_relevant_messages(b: RelevantMessagesRequest, chat_id: int|None = None):
    if chat_id is None:
        return {123: "биба боба"}
    return {chat_id: "биба боба"}


@app.post("/messages")
def add_messages(request: AddingMessagesRequest):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "success",
            "added_messages": len(request.messages)
        }
    )


class SummarizationReq(BaseModel):
    prompt: str


class DraftReq(BaseModel):
    messages: list[dict]


@app.post("/summarize")
def summarize(req: SummarizationReq):
    return f"результат суммаризации"


@app.post("/draft")
def summarize(req: DraftReq):
    return f"черновик сообщения"
