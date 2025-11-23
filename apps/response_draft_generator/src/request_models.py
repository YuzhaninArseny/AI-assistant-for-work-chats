from typing import List, Dict
from pydantic import BaseModel


class ResponseDraftGeneratorRequest(BaseModel):
    messages: List[Dict]