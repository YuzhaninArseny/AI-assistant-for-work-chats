import datetime
from typing import Iterable

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from apps.command_service.src.command_service_app.main import app
from apps.shared.src.shared.db.database import get_session
from apps.shared.src.shared.models.messages import Message
from command_service_app.repositories.db_client import get_client
from shared.models.base import Base

get_summarization_model = ...  # импортировать реальную зависимость из кода


class FakeModel:
    def summarize(self, chat_id, limit):
        return f"Эффективная суммаризация для чата {chat_id}, лимит {limit}"


class FakeClient:
    def get_chat_messages(self, chat_id: int, limit: int | None = None) -> Iterable[Message]:
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
    return FakeModel()


def fake_get_client():
    return FakeClient()


@pytest.fixture
def deps_setup():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_client] = fake_get_client
    app.dependency_overrides[get_summarization_model] = get_summ_model_override
    yield
    app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)


@pytest.mark.xfail
def test_summarize(deps_setup):
    client = TestClient(app)
    chat_id = 1
    limit = None
    response = client.get(
        "/summarize",
        params={"chat_id": chat_id}
    )

    data = response.text
    print(data)
    assert response.status_code == 200
    assert data == f"Эффективная суммаризация для чата {chat_id}, лимит {limit}"
