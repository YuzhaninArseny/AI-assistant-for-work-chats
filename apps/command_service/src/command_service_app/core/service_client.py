from typing import Any, Dict
import httpx


class ServiceClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
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


# Инициализация клиентов
summarization_client = ServiceClient("http://summarizator:8083")
chroma_service_client = ServiceClient("http://chroma:8082")
response_draft_generator_client = ServiceClient("http://response-draft-generator:8084")


# Использование
async def process_text(text: str):
    summary = await summarization_client.post("/summarize", json={"text": text})
    return {"summary": summary}