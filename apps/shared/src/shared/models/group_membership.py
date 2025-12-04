from sqlmodel import SQLModel, Field


class GroupMembership(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    group_id: int


class Group(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
