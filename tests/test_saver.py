from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from apps.saver.src.saver_app.main import app
from apps.shared.src.shared.db.database import get_session
from apps.shared.src.shared.schemas.TelegramApiDtos import TelegramMessage


def test_create_hero():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        client = TestClient(app)
        message = TelegramMessage()
        response = client.post(
            "/heroes/",
            json=message
        )
        app.dependency_overrides.clear()
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == "Deadpond"
        assert data["secret_name"] == "Dive Wilson"
        assert data["age"] is None
        assert data["id"] is not None
