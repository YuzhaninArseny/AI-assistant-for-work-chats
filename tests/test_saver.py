import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from apps.saver.src.saver_app.main import app
from apps.shared.src.shared.db.database import get_session
from apps.shared.src.shared.schemas.TelegramApiDtos import TelegramMessage, TelegramChat, TelegramUser
from shared.models.base import Base


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


def test_send_message(db_setup):
    client = TestClient(app)
    message = TelegramMessage(
        message_id=1,
        chat=TelegramChat(id=123, title="тестовый чат"),
        date=int(datetime.datetime(year=2025, month=1, day=1).timestamp()),
        from_=TelegramUser(id=987, name="admin")

    )
    response = client.post(
        "/messages",
        json=message.model_dump()
    )

    data = response.json()
    print(response.json())
    assert response.status_code == 201
    assert data == message.model_dump()
