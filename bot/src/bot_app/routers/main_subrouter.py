import logging

from aiogram import Router, Bot
from aiogram.filters import CommandStart, ChatMemberUpdatedFilter, JOIN_TRANSITION, CommandObject
from aiogram.types import Message, ChatMemberUpdated
from aiohttp import ClientSession

from bot_app.api.api import save_message
from bot_app.api.subscriptions import subscribe_user

router = Router()


@router.message(CommandStart(deep_link=True))
async def start(message: Message, command: CommandObject):
    try:
        group_id = int(command.args)
    except ValueError:
        await message.answer("Некорректная ссылка")
        return

    logging.info(f"Subscription request: {group_id}")
    await subscribe_user(message.from_user.id, group_id)

    # TODO: получать реальное название, а не айди
    group_name = command.args
    await message.answer(f"Вы подписаны на группу {group_name}")


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("стартанули")


@router.message()
async def msg(message: Message, aiohttp_session: ClientSession):
    if message.chat.type in {"group", "supergroup"}:
        await save_message(aiohttp_session, message)
    else:
        await message.answer(f": {message.text}")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added(event: ChatMemberUpdated, bot: Bot):
    # TODO: запрос на бэкэнд
    logging.info(f"Bot added to {event.chat.type} {event.chat.id}")
    await event.answer(f"Теперь для этой группы можно делать краткие сводки с помощью бота.\n\n"
                       f"[Ссылка для добавления в бота](https://t.me/workchat_assistant_bot?start={event.chat.id})", parse_mode='markdown')
