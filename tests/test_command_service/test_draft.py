import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from apps.command_service.src.command_service_app.main import app
from apps.shared.src.shared.models.messages import Message
from command_service_app.api.routes.draft import get_draft_client
from command_service_app.repositories.db_client import get_session
from shared.models.base import Base


class FakeDraftClient:
    async def post(self, url: str, json: dict):
        assert url in {"/draft", "/draft/"}
        assert json['messages']
        for msg in json['messages']:
            assert msg.get('content')

        # ServiceClient возвращает обычные объекты, а не json-репрезентацию
        # поэтому это строка без кавычек внутри
        return 'это фейковый текст драфта'


def get_fake_draft_client():
    return FakeDraftClient()


@pytest.fixture
def deps_setup():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_draft_client] = get_fake_draft_client
    yield
    app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)


def add_test_messages(session, chat_id):
    msg = Message(
        message_id=1,
        chat_id=chat_id,
        time_sent=datetime.datetime(year=2025, month=1, day=1),
        user_id=987,
        username="admin",
        content=f"msg content"
    )
    session.add(msg)
    session.commit()


# @pytest.mark.parametrize("with_messages", [False, True])
# def test_draft(deps_setup, with_messages):
#     client = TestClient(app)
#     db_session = app.dependency_overrides[get_session]()
#     if with_messages:
#         add_test_messages(db_session, 123)
#
#     response = client.get(
#         "/draft/",
#         params={"chat_id": 123}
#     )
#
#     data = response.json()
#     assert response.status_code == 200
#     if with_messages:
#         assert data == 'это фейковый текст драфта'
#     else:
#         assert data == "Невозможно составить черновик ответа - вопросов не обнаружено"
