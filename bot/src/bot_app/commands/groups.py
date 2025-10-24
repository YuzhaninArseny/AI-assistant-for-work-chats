import math

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from bot_app.api.subscriptions import get_user_groups, GroupInfo, unsubscribe_user

router = Router()

GROUP_PAGE_SIZE = 5
ACTION_PAGE = "page"
ACTION_VIEW_GROUP = "group"
ACTION_UNSUBSCRIBE = "unsub"
ACTION_EMPTY = ""


class GroupsCBDataFactory(CallbackData, prefix='groups'):
    action: str
    payload: int


def create_kb(groups: list[GroupInfo], current_page=1):
    page_count = math.ceil(len(groups) / GROUP_PAGE_SIZE)

    keyborad_builder = InlineKeyboardBuilder()
    buttons = []
    offset = GROUP_PAGE_SIZE * (current_page - 1)
    page_groups = groups[offset:offset + GROUP_PAGE_SIZE]
    for group in page_groups:
        buttons.append(InlineKeyboardButton(
            text=group.name,
            callback_data=GroupsCBDataFactory(action=ACTION_VIEW_GROUP, payload=group.id).pack()
        ))

    keyborad_builder.row(*buttons, width=1)

    footer_buttons = []

    if current_page > 1:
        footer_buttons.append(InlineKeyboardButton(
            text="<-",
            callback_data=GroupsCBDataFactory(action=ACTION_PAGE, payload=current_page - 1).pack()
        ))
    footer_buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{page_count}",
        callback_data=GroupsCBDataFactory(action=ACTION_EMPTY, payload=0).pack()
    ))
    if current_page < page_count:
        footer_buttons.append(InlineKeyboardButton(
            text="->",
            callback_data=GroupsCBDataFactory(action=ACTION_PAGE, payload=current_page + 1).pack()
        ))

    keyborad_builder.row(*footer_buttons)
    return keyborad_builder.as_markup()


@router.message(Command("groups"))
async def add_group(message: Message):
    groups = await get_user_groups(message.from_user.id)
    if groups:
        buttons_markup = create_kb(groups)
        await message.answer("Группы, на обновления в которых вы подписаны:", reply_markup=buttons_markup)
    else:
        await message.answer("Вы пока не добавили никаких групп. "
                             "Воспользуйтесь ссылкой для добавления группы в бота")


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_PAGE))
async def group_page_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory):
    markup = create_kb(await get_user_groups(callback.message.from_user.id), callback_data.payload)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer(callback.data)


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_VIEW_GROUP))
async def group_view_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory):
    keyborad_builder = InlineKeyboardBuilder()
    keyborad_builder.row(InlineKeyboardButton(
        text="Unsubscribe",
        callback_data=GroupsCBDataFactory(action=ACTION_UNSUBSCRIBE, payload=callback_data.payload).pack()
    ))
    markup = keyborad_builder.as_markup()
    await callback.message.answer(f"Инфо про группу {callback_data.payload}", reply_markup=markup)
    await callback.answer()


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_UNSUBSCRIBE))
async def group_unsub_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory):
    # TODO: error handling
    await unsubscribe_user(callback.from_user.id, callback_data.payload)
    await callback.message.answer(f"Вы отписаны от группы")
    await callback.answer()


@router.callback_query(GroupsCBDataFactory.filter(F.action == ACTION_EMPTY))
async def group_nop_cb(callback: CallbackQuery, callback_data: GroupsCBDataFactory):
    await callback.answer()
