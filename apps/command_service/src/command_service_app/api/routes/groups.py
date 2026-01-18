from logging import getLogger, INFO

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from command_service_app.repositories.db_client import SessionDep
from shared.models.group_membership import GroupMembership, Group

router = APIRouter(prefix="/groups", tags=["groups"])

logger = getLogger("command")
logger.setLevel(INFO)


@router.post("/add-bot")
def add_bot_to_group(session: SessionDep, group: Group):
    logger.info(f"Adding bot to group {group.id}")
    if session.get(Group, group.id) is not None:
        logger.info(f"Group already added: {group.id}")
        return
    session.add(group)
    session.commit()


@router.post("/add-user")
def add_user_to_group(session: SessionDep, user_id: int, group_id: int):
    logger.info(f"Adding user {user_id} to group {group_id}")
    if session.get(Group, group_id) is None:
        raise HTTPException(400, "Unknown group")
    session.add(GroupMembership(user_id=user_id, group_id=group_id))
    session.commit()


@router.post("/remove-user")
def add_user_to_group(session: SessionDep, user_id: int, group_id: int):
    logger.info(f"Removing user {user_id} from group {group_id}")
    select_query = select(GroupMembership).where(GroupMembership.user_id == user_id,
                                                 GroupMembership.group_id == group_id)
    user_membership = session.exec(select_query).first()
    if user_membership is None:
        raise HTTPException(400, "User was not subscribed")
    session.delete(user_membership)
    session.commit()


@router.get("/my")
def my_groups(session: SessionDep, user_id: int):
    logger.info(f"Reading user groups: {user_id}")
    query = (select(Group).join(GroupMembership, GroupMembership.group_id == Group.id)
             .where(GroupMembership.user_id == user_id))
    return session.exec(query).all()


@router.get('/{group_id}')
def get_group_info(session: SessionDep, group_id: int):
    return session.get(Group, group_id)
