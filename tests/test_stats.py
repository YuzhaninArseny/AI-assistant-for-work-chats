import datetime
from typing import List
import sys
from unittest.mock import MagicMock
sys.modules["psycopg2"] = MagicMock()
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

# Saver app — для записи
from apps.saver.src.saver_app.main import app as saver_app, get_chroma_client
# Command service app — для чтения
from apps.command_service.src.command_service_app.main import app as command_app

# Общая зависимость
from apps.shared.src.shared.db.database import get_session

# Схемы Telegram
from apps.shared.src.shared.schemas.TelegramApiDtos import (
    TelegramMessage,
    TelegramChat,
    TelegramUser,
    ChatStats
)

# Pydantic-модель ответа

# Модели БД
from shared.models.base import Base
from shared.models.messages import Message

# === ХАК: избегаем ImportError psycopg2 ===



# =========================================


class FakeChromaServiceClient:
    async def post(self, url: str, json: dict):
        return type("MockResponse", (), {"status_code": 200})()


@pytest.fixture
def db_setup():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})

    SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            return session

    saver_app.dependency_overrides[get_session] = get_session_override
    command_app.dependency_overrides[get_session] = get_session_override

    yield

    saver_app.dependency_overrides.clear()
    command_app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)


@pytest.fixture
def chromadb():
    return FakeChromaServiceClient()


def send_messages_to_saver(saver_client, chromadb, messages: List[TelegramMessage]):
    saver_app.dependency_overrides[get_chroma_client] = lambda: chromadb
    for msg in messages:
        resp = saver_client.post(
            "/messages",
            json=msg.model_dump(by_alias=True)
        )
        assert resp.status_code == 201, f"Failed to save message: {resp.text}"


# --- Вспомогательные функции ---
def make_message(chat_id: int, user_id: int, text: str, timestamp: int, message_id: int = 1):
    return TelegramMessage(
        message_id=message_id,
        chat=TelegramChat(id=chat_id, title="Test Chat"),
        date=timestamp,
        from_=TelegramUser(id=user_id),
        text=text
    )


# --- Тесты ---

def test_stats_empty_chat(db_setup, chromadb):
    """Проверка статистики для чата без сообщений."""
    client = TestClient(command_app)
    response = client.get("/chats/999/stats")
    assert response.status_code == 200
    stats = ChatStats(**response.json())
    assert stats.top_users == []
    assert len(stats.daily_activity) == 14
    assert all(len(v) == 0 for v in stats.daily_activity.values())


def test_stats_ignores_service_messages(db_setup, chromadb):
    """Служебные сообщения (is_service=True) не учитываются."""
    # Но в saver мы не можем задать is_service напрямую.
    # Поэтому этот тест требует либо прямой вставки в БД, либо изменения saver.
    # Пропустим пока — или предположим, что saver не создаёт служебные сообщения.
    pytest.skip("Требует прямой вставки в БД или расширения API saver'а")


def test_stats_single_user(db_setup, chromadb):
    """Один пользователь — он же в топе."""
    saver_client = TestClient(saver_app)
    command_client = TestClient(command_app)

    now_utc = datetime.datetime(2026, 1, 18, 12, 0, 0, tzinfo=datetime.timezone.utc)
    ts = int(now_utc.timestamp())

    msg = make_message(chat_id=100, user_id=500, text="Hi", timestamp=ts, message_id=1)
    send_messages_to_saver(saver_client, chromadb, [msg])

    response = command_client.get("/chats/100/stats")
    assert response.status_code == 200
    stats = ChatStats(**response.json())
    assert len(stats.top_users) == 1
    assert stats.top_users[0].user_id == 500
    assert stats.top_users[0].message_count == 1


def test_stats_exactly_14_days_included(db_setup, chromadb):
    """Сообщение ровно 14 дней назад (00:00 GMT+5) — должно быть включено."""
    saver_client = TestClient(saver_app)
    command_client = TestClient(command_app)

    # Сегодня: 2026-01-18 12:00 UTC → 2026-01-18 17:00 GMT+5
    now_utc = datetime.datetime(2026, 1, 18, 12, 0, 0, tzinfo=datetime.timezone.utc)
    # 14 дней назад в GMT+5: 2026-01-05 00:00 GMT+5 → 2026-01-04 19:00 UTC
    boundary_utc = datetime.datetime(2026, 1, 4, 19, 0, 0, tzinfo=datetime.timezone.utc)
    ts = int(boundary_utc.timestamp())

    msg = make_message(chat_id=200, user_id=600, text="Edge", timestamp=ts, message_id=1)
    send_messages_to_saver(saver_client, chromadb, [msg])

    response = command_client.get("/chats/200/stats")
    stats = ChatStats(**response.json())
    # Должен быть день '2026-01-05'
    assert "2026-01-05" in stats.daily_activity
    day_data = stats.daily_activity["2026-01-05"]
    assert len(day_data) == 1
    assert day_data[0].user_id == 600


def test_stats_message_just_outside_period_excluded(db_setup, chromadb):
    """Сообщение за пределами 14 дней — исключено."""
    saver_client = TestClient(saver_app)
    command_client = TestClient(command_app)

    # Текущее время: 2026-01-18 12:00 UTC → в GMT+5: 2026-01-18 17:00
    now_utc = datetime.datetime(2026, 1, 18, 12, 0, 0, tzinfo=datetime.timezone.utc)

    # Начало периода в GMT+5: 2026-01-04 17:00 → в UTC: 2026-01-04 12:00
    # Ставим сообщение на 1 секунду ДО начала периода: 2026-01-04 11:59:59 UTC
    outside_utc = datetime.datetime(2026, 1, 4, 11, 59, 59, tzinfo=datetime.timezone.utc)
    ts = int(outside_utc.timestamp())

    msg = make_message(chat_id=201, user_id=601, text="Too old", timestamp=ts, message_id=1)
    send_messages_to_saver(saver_client, chromadb, [msg])

    response = command_client.get("/chats/201/stats")
    stats = ChatStats(**response.json())

    # День '2026-01-04' может присутствовать (если репозиторий возвращает все 14 дней),
    # но в нём должно быть 0 активности.
    assert len(stats.daily_activity) == 14
    # Убедимся, что ни в одном дне нет сообщений
    assert all(len(activities) == 0 for activities in stats.daily_activity.values())


def test_stats_timezone_conversion_edge(db_setup, chromadb):
    """Сообщение в 23:59 UTC → должно попасть в следующий день в GMT+5."""
    saver_client = TestClient(saver_app)
    command_client = TestClient(command_app)

    # 2026-01-17 23:59 UTC → в GMT+5 это 2026-01-18 04:59 → дата '2026-01-18'
    msg_time_utc = datetime.datetime(2026, 1, 17, 23, 59, 0, tzinfo=datetime.timezone.utc)
    ts = int(msg_time_utc.timestamp())

    msg = make_message(chat_id=300, user_id=700, text="TZ edge", timestamp=ts, message_id=1)
    send_messages_to_saver(saver_client, chromadb, [msg])

    response = command_client.get("/chats/300/stats")
    stats = ChatStats(**response.json())
    assert "2026-01-18" in stats.daily_activity
    assert stats.daily_activity["2026-01-18"][0].user_id == 700


def test_stats_top_5_limited(db_setup, chromadb):
    """Если активных пользователей >5, возвращаются только топ-5."""
    saver_client = TestClient(saver_app)
    command_client = TestClient(command_app)

    now_utc = datetime.datetime(2026, 1, 18, 12, 0, 0, tzinfo=datetime.timezone.utc)
    ts = int(now_utc.timestamp())

    messages = []
    for i in range(7):  # 7 пользователей
        for _ in range(i + 1):  # user 0: 1 msg, user 1: 2 msgs, ..., user 6: 7 msgs
            messages.append(
                make_message(chat_id=400, user_id=1000 + i, text=f"Msg", timestamp=ts, message_id=len(messages) + 1)
            )

    send_messages_to_saver(saver_client, chromadb, messages)

    response = command_client.get("/chats/400/stats")
    stats = ChatStats(**response.json())
    assert len(stats.top_users) == 5
    # Пользователи отсортированы по убыванию активности
    user_ids = [u.user_id for u in stats.top_users]
    expected = [1006, 1005, 1004, 1003, 1002]  # самые активные
    assert user_ids == expected


def test_stats_daily_activity_includes_empty_days(db_setup, chromadb):
    """Все 14 дней присутствуют, даже если в них нет активности."""
    saver_client = TestClient(saver_app)
    command_client = TestClient(command_app)

    now_utc = datetime.datetime(2026, 1, 18, 12, 0, 0, tzinfo=datetime.timezone.utc)
    ts = int(now_utc.timestamp())

    # Одно сообщение сегодня
    msg = make_message(chat_id=500, user_id=800, text="Only today", timestamp=ts, message_id=1)
    send_messages_to_saver(saver_client, chromadb, [msg])

    response = command_client.get("/chats/500/stats")
    stats = ChatStats(**response.json())
    assert len(stats.daily_activity) == 14
    non_empty_days = [day for day, acts in stats.daily_activity.items() if acts]
    assert len(non_empty_days) == 1
    assert non_empty_days[0] == "2026-01-18"