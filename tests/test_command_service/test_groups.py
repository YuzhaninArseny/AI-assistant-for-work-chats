import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from apps.command_service.src.command_service_app.main import app
from command_service_app.repositories.db_client import get_session
from shared.models.base import Base
from shared.models.group_membership import GroupMembership, Group


@pytest.fixture
def deps_setup():
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


def add_groups(session: Session):
    session.add(Group(
        id=1,
        title="test group A"
    ))
    session.add(Group(
        id=2,
        title="test group B"
    ))
    session.add(Group(
        id=3,
        title="test group C"
    ))
    session.add(Group(
        id=987,
        title="the secret group"
    ))
    session.commit()


def add_group_memberships(session: Session):
    session.add(GroupMembership(
        user_id=123,
        group_id=1
    ))
    session.add(GroupMembership(
        user_id=123,
        group_id=3
    ))
    session.commit()


def test_addbot(deps_setup):
    client = TestClient(app)
    session: Session = app.dependency_overrides[get_session]()

    response = client.post(
        "/groups/add-bot",
        json={"id": 123, "title": "aaa"}
    )
    assert response.status_code == 200

    members = session.exec(select(Group)).all()
    assert len(members) == 1
    assert members[0].id == 123
    assert members[0].title == "aaa"


def test_adduser(deps_setup):
    client = TestClient(app)
    session: Session = app.dependency_overrides[get_session]()
    add_groups(session)
    response = client.post(
        "/groups/add-user",
        params={"user_id": 123, "group_id": 987}
    )
    assert response.status_code == 200

    members = session.exec(select(GroupMembership)).all()
    assert len(members) == 1
    assert members[0].user_id == 123
    assert members[0].group_id == 987


def test_get_groups_ok(deps_setup):
    client = TestClient(app)
    session: Session = app.dependency_overrides[get_session]()
    add_groups(session)
    add_group_memberships(session)
    response = client.get(
        "/groups/my",
        params={"user_id": 123}
    )
    data = response.json()

    assert response.status_code == 200
    assert data == [
        {'title': 'test group A', 'id': 1},
        {'title': 'test group C', 'id': 3}
    ]


def test_get_groups_empty(deps_setup):
    client = TestClient(app)
    session: Session = app.dependency_overrides[get_session]()
    add_group_memberships(session)
    response = client.get(
        "/groups/my",
        params={"user_id": 9}
    )
    data = response.json()

    assert response.status_code == 200
    assert data == []
