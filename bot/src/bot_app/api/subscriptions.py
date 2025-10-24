from pydantic import BaseModel


class GroupInfo(BaseModel):
    id: int
    name: str


async def subscribe_user(user_id: int, group_id: int):
    # TODO: INSERT user INTO subscriptions
    pass


async def unsubscribe_user(user_id: int, group_id: int):
    # TODO: DELETE user FROM subscriptions
    pass


async def get_user_groups(user_id: int) -> list[GroupInfo]:
    # TODO: query db
    return [GroupInfo(id=i, name=f"my cool group {i}") for i in range(12)]
