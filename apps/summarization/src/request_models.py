from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    prompt: str