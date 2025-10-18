import os
from contextlib import asynccontextmanager
from typing import Iterable, Annotated

from fastapi import Depends, FastAPI
from sqlmodel import select, Session, desc, create_engine, SQLModel

from message import Message

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SCHEME = "postgresql"  # os.getenv("DB_SCHEME")
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_USER = os.getenv('DB_USER')
DB_NAME = os.getenv('DB_NAME')

db_url = f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)


def get_session():
    with Session(engine) as s:
        yield s


@asynccontextmanager
async def load_db_lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


class DbClient:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get_chat_messages(self, chat_id: int, limit: int | None = None) -> Iterable[Message]:
        query = select(Message).where(Message.chat_id == chat_id).order_by(desc(Message.time_sent))
        if limit is not None:
            query = query.limit(limit)

        return self.session.exec(query).all()


SessionDep = Annotated[Session, Depends(get_session)]


def get_client(session: SessionDep):
    return DbClient(session)


DbClientDep = Annotated[DbClient, Depends(get_client)]
