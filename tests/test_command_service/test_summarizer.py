import datetime
from typing import Iterable

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from apps.command_service.src.command_service_app.main import app
from apps.shared.src.shared.db.database import get_session
from apps.shared.src.shared.models.messages import Message
from command_service_app.api.routes.summarize import get_summarization_model
from command_service_app.repositories.db_client import get_client
from shared.models.base import Base


class FakeSummarizationModel:
    async def post(self, endpoint: str, json: dict):
        assert endpoint == "/summarize"
        assert json['prompt']
        return "Эффективная суммаризация для чата"


class FakeDbClient:
    fill: bool

    def __init__(self, fill: bool):
        self.fill = fill

    def get_chat_messages(self, chat_id: int, limit: int | None = None) -> Iterable[Message]:
        if not self.fill:
            return []

        return [
            Message(
                message_id=i,
                chat_id=chat_id,
                time_sent=datetime.datetime(year=2025, month=1, day=1),
                user_id=987,
                username="admin",
                content=f"msg {i}"
            )
            for i in range(limit or 10)
        ]


def get_summ_model_override():
    return FakeSummarizationModel()


@pytest.fixture
def deps_setup():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_summarization_model] = get_summ_model_override
    yield
    app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)


@pytest.mark.parametrize("with_messages", [True, False], ids=['With messages', 'Without messages'])
def test_summarize(deps_setup, with_messages):
    client = TestClient(app)

    def fake_get_db_client():
        return FakeDbClient(with_messages)

    app.dependency_overrides[get_client] = fake_get_db_client
    chat_id = 1
    limit = None
    response = client.get(
        "/summarize",
        params={"chat_id": chat_id}
    )

    data = response.text
    assert response.status_code == 200

    # по дефолту фастапи возвращает JSON,
    # поэтому мы получаем не просто текст, а JSON строку
    if with_messages:
        assert data == '"Эффективная суммаризация для чата"'
    else:
        assert data == '"В чате нет активности"'
