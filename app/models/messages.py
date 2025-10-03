from __future__ import annotations
from datetime import datetime
from typing import Optional, Any, Dict

from sqlalchemy import (
    BigInteger, DateTime, String, Text, UniqueConstraint,
    Index, func, event, DDL, Boolean
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, Field
from app.models.base import Base

class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        UniqueConstraint('chat_id', 'message_id', name='uq_chat_msg'),
        # Индекс для FTS
        Index("ix_messages_tsv", "tsv", postgresql_using="gin"),
        # триграммный индекс для ILIKE/опечаток
        Index(
            "ix_messages_content_trgm",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"}
        ),
        Index("ix_messages_chat_time", "chat_id", "time_sent"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, index=True)

    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_service: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reply_to_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)
    forward_from_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)


    time_sent: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    time_loaded: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    tsv: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)

