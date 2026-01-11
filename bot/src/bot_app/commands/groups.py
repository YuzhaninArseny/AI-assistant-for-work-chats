from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import ClientSession
from magic_filter import F

from bot_app.api.subscriptions import get_user_groups, unsubscribe_user
from bot_app.commands.groups_kb import ACTION_PAGE, ACTION_VIEW_GROUP, ACTION_UNSUBSCRIBE, ACTION_EMPTY, \
    create_kb, get_group_name

router = Router()


class GroupsCBDataFactory(CallbackData, prefix='groups'):
    action: str
    payload: int


@router.message(Command("groups"))
async def add_group(message: Message, aiohttp_session: ClientSession, state: FSMContext):
    groups = await get_user_groups(aiohttp_session, message.from_user.id)
    if groups:
        buttons_markup = await create_kb(groups, ACTION_VIEW_GROUP, GroupsCBDataFactory, state)
        await message.answer("Группы, на обновления в которых вы подписаны:", reply_markup=buttons_markup)
    else:
        await message.answer("Вы пока не добавили никаких групп. "
                             "Воспользуйтесь ссылкой для добавления группы в бота")


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_PAGE))
async def group_page_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory,
                        aiohttp_session: ClientSession, state: FSMContext):
    markup = create_kb(await get_user_groups(aiohttp_session, callback.message.from_user.id),
                       ACTION_VIEW_GROUP,
                       GroupsCBDataFactory,
                       state,
                       current_page=callback_data.payload)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer(callback.data)


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_VIEW_GROUP))
async def group_view_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory, state: FSMContext):
    keyborad_builder = InlineKeyboardBuilder()
    keyborad_builder.row(InlineKeyboardButton(
        text="Unsubscribe",
        callback_data=GroupsCBDataFactory(action=ACTION_UNSUBSCRIBE, payload=callback_data.payload).pack()
    ))
    markup = keyborad_builder.as_markup()

    group_name = get_group_name(callback_data.payload, await state.get_value("page_groups"))
    await callback.message.answer(f"Инфо про группу {group_name}", reply_markup=markup)
    await callback.answer()


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_UNSUBSCRIBE))
async def group_unsub_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory, aiohttp_session: ClientSession):
    # TODO: error handling
    success = await unsubscribe_user(aiohttp_session, callback.from_user.id, callback_data.payload)
    if success:
        await callback.message.answer(f"Вы отписаны от группы")
    else:
        await callback.message.answer(f"Произошла ошибка")
    await callback.answer()


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_EMPTY))
async def group_nop_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory):
    await callback.answer()
