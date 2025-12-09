import datetime
from typing import Iterable

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from apps.command_service.src.command_service_app.main import app
from apps.shared.src.shared.db.database import get_session
from apps.shared.src.shared.models.messages import Message
from command_service_app.api.routes.relevant_messages import get_chroma_client
from shared.models.base import Base


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
                content=f"msg {i}",
                chat_title="test"
            )
            for i in range(limit or 10)
        ]


fake_chat_messages = {
    987: {
        1: {"text": "Привет"},
        2: {"text": "Ого, привет, ты тоже пользуешься этим мессенджером"},
    },
    654: {
        3: {"text": "Здравствуй"},
        4: {"text": "Приветик"},
    }
}


class FakeChroma:
    async def post(self, a, json):
        assert a == "/relevant-messages"
        print(a)
        print(json)
        print(fake_chat_messages)
        return fake_chat_messages


def get_fake_chroma_client():
    return FakeChroma()


@pytest.fixture
def deps_setup():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_chroma_client] = get_fake_chroma_client
    yield
    app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)


def test_search(deps_setup):
    client = TestClient(app)

    response = client.post(
        "/relevant-messages",
        json={"key_words": ["привет"]}
    )

    data = response.json()
    print(data)
    assert response.status_code == 200

    assert len(data) == 2
    assert len(data['987']) == 2
    assert len(data['654']) == 2
    assert data['987']['1']['text'] == "Привет"
    assert data['987']['2']['text'] == "Ого, привет, ты тоже пользуешься этим мессенджером"
    assert data['654']['3']['text'] == "Здравствуй"
    assert data['654']['4']['text'] == "Приветик"


@pytest.mark.parametrize("chat_id", [987, 654])
def test_search_for_chat(deps_setup, chat_id):
    client = TestClient(app)

    chat_ids = [987, 654]

    for chat_id in chat_ids:
        response = client.post(
            "/relevant-messages",
            json={"key_words": ["привет"]},
            params={"chat_id": chat_id}
        )

        data = response.json()
        print(data)
        assert response.status_code == 200

        assert len(data) == 1
        assert len(data[str(chat_id)]) == 2

        for other_chat_id in chat_ids:
            if other_chat_id == chat_id:
                continue
            assert len(data.get(str(other_chat_id), [])) == 0

        for msg_id in fake_chat_messages[chat_id]:
            assert data[str(chat_id)][str(msg_id)]['text'] == fake_chat_messages[chat_id][msg_id]['text']
