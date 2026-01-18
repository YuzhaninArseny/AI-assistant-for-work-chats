import logging

from aiogram import Router, Bot
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, JOIN_TRANSITION, CommandObject
from aiogram.types import Message, ChatMemberUpdated
from aiohttp import ClientSession

from bot_app.api.api import save_message
from bot_app.api.subscriptions import subscribe_user, add_bot, get_group_name

router = Router()


@router.message(CommandStart(deep_link=True))
async def start(message: Message, command: CommandObject, aiohttp_session: ClientSession):
    try:
        group_id = int(command.args)
    except ValueError:
        await message.answer("Некорректная ссылка")
        return

    logging.info(f"Subscription request: {group_id}")
    await subscribe_user(aiohttp_session, message.from_user.id, group_id)
    group_name = await get_group_name(aiohttp_session, group_id)
    await message.answer(f"Вы подписаны на группу {group_name}")


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("стартанули")


@router.message()
async def msg(message: Message, aiohttp_session: ClientSession):
    if message.chat.type in {"group", "supergroup"}:
        await save_message(aiohttp_session, message)
    else:
        await message.answer("Неизвестная команда. Выберите команду из меню")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added(event: ChatMemberUpdated, bot: Bot, aiohttp_session: ClientSession):
    await add_bot(aiohttp_session, {"id": event.chat.id, "title": event.chat.title})
    logging.info(f"Bot added to {event.chat.type} {event.chat.id}")
    await event.answer(f"Теперь для этой группы можно делать краткие сводки с помощью бота.\n\n"
                       f"[Ссылка для добавления в бота](https://t.me/workchat_assistant_bot?start={event.chat.id})",
                       parse_mode='markdown')
