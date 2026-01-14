import os
from typing import Any, Dict
import httpx


class ServiceClient:
    def __init__(self, base_url: str, timeout: float = 600.0):
        self.base_url = base_url
        self.timeout = timeout

    async def post(self, endpoint: str, **kwargs) -> Any:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.post(endpoint, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str, **kwargs) -> Any:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.get(endpoint, **kwargs)
            response.raise_for_status()
            return response.json()


CHROMA_HOST = os.getenv("CHROMA_HOST") or "chroma:8082"
SUMMARIZER_HOST = os.getenv("SUMMARIZER_HOST") or "summarizator:8083"
DRAFT_HOST = os.getenv("DRAFT_HOST") or "response-draft-generator:8084"
# Инициализация клиентов
summarization_client = ServiceClient(f"http://{SUMMARIZER_HOST}")
chroma_service_client = ServiceClient(f"http://{CHROMA_HOST}")
response_draft_generator_client = ServiceClient(f"http://{DRAFT_HOST}")


# Использование
async def process_text(text: str):
    summary = await summarization_client.post("/summarize", json={"text": text})
    return {"summary": summary}