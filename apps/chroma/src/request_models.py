from typing import List, Dict
from pydantic import BaseModel


class RelevantMessagesRequest(BaseModel):
    key_words: List[str]


class AddingMessagesRequest(BaseModel):
    messages: List[Dict]
