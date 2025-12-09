import logging

from aiohttp import ClientSession
from pydantic import BaseModel

from bot_app.api.api import command_base_url


class GroupInfo(BaseModel):
    id: int
    name: str


async def subscribe_user(aios: ClientSession, user_id: int, group_id: int):
    resp = await aios.post(
        f"{command_base_url}/groups/add-user",
        params={"user_id": user_id, "group_id": group_id}
    )
    if resp.status != 200:
        logging.error(resp.text)


async def add_bot(aios: ClientSession, group: dict):
    resp = await aios.post(
        f"{command_base_url}/groups/add-bot",
        json=group
    )
    if resp.status != 200:
        logging.error(resp.text)


async def unsubscribe_user(aios: ClientSession, user_id: int, group_id: int) -> bool:
    resp = await aios.post(
        f"{command_base_url}/groups/remove-user",
        params={"user_id": user_id, "group_id": group_id}
    )
    if resp.status != 200:
        logging.error(resp.text)
        return False
    return True


async def get_user_groups(aios: ClientSession, user_id: int) -> list[GroupInfo]:
    resp = await aios.get(
        f"{command_base_url}/groups/my",
        params={"user_id": user_id}
    )
    if resp.status != 200:
        logging.error(resp.text)

    return [GroupInfo(id=group['id'], name=group['title']) for group in await resp.json()]
