from sqlalchemy import Column, BigInteger
from sqlmodel import SQLModel, Field


class GroupMembership(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(sa_column=Column(BigInteger()))
    group_id: int = Field(sa_column=Column(BigInteger()))


class Group(SQLModel, table=True):
    id: int = Field(sa_column=Column(BigInteger(), primary_key=True))
    title: str
