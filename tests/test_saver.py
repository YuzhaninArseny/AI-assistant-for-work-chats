import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from apps.saver.src.saver_app.main import app, get_chroma_client
from apps.shared.src.shared.db.database import get_session
from apps.shared.src.shared.schemas.TelegramApiDtos import TelegramMessage, TelegramChat, TelegramUser
from shared.models.base import Base


class FakeChromaServiceClient:
    documents: list[dict]

    def __init__(self):
        self.documents = []

    async def post(self, url: str, json: dict):
        print("ABOBA")
        assert url in {"/messages", "/messages/"}

        for msg in json['messages']:
            self.documents.append({
                'text': msg['text'],
                'message_id': str(msg['message_id']),
                'chat_id': str(msg['chat']['id']),
                'timestamp': msg['date'],
            })


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def chromadb():
    return FakeChromaServiceClient()


@pytest.fixture
def db_setup():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            return session

    app.dependency_overrides[get_session] = get_session_override
    yield
    app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)


TEST_TIMESTAMP = datetime.datetime(year=2025, month=1, day=1).timestamp()


def send_message(client_, timestamp, chromadb):
    def get_fake_chroma_client():
        return chromadb

    app.dependency_overrides[get_chroma_client] = get_fake_chroma_client
    message = TelegramMessage(
        message_id=1,
        chat=TelegramChat(id=123, title="тестовый чат"),
        date=int(timestamp),
        from_=TelegramUser(id=987, name="admin"),
        text="Здравствуй"
    )
    response = client_.post(
        "/messages",
        json=message.model_dump()
    )
    return message, response


def test_saves_to_db(db_setup, client, chromadb):
    message, response = send_message(client, TEST_TIMESTAMP, chromadb)
    data = response.json()

    assert response.status_code == 201
    assert data == message.model_dump(by_alias=True)


def test_saves_to_chroma(db_setup, client, chromadb):
    message, response = send_message(client, TEST_TIMESTAMP, chromadb)

    assert response.status_code == 201
    assert chromadb.documents == [
        {
            'text': "Здравствуй",
            'message_id': '1',
            'chat_id': '123',
            'timestamp': TEST_TIMESTAMP,
        }
    ]
