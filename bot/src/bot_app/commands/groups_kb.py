import math

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot_app.api.subscriptions import GroupInfo

GROUP_PAGE_SIZE = 5
ACTION_PAGE = "page"
ACTION_VIEW_GROUP = "group"
ACTION_UNSUBSCRIBE = "unsub"
ACTION_EMPTY = ""


def create_kb(groups: list[GroupInfo], click_action, cb_factory, *, current_page=1):
    page_count = math.ceil(len(groups) / GROUP_PAGE_SIZE)

    keyborad_builder = InlineKeyboardBuilder()
    buttons = []
    offset = GROUP_PAGE_SIZE * (current_page - 1)
    page_groups = groups[offset:offset + GROUP_PAGE_SIZE]
    for group in page_groups:
        buttons.append(InlineKeyboardButton(
            text=group.name,
            callback_data=cb_factory(action=click_action, payload=group.id).pack()
        ))

    keyborad_builder.row(*buttons, width=1)

    footer_buttons = []

    if current_page > 1:
        footer_buttons.append(InlineKeyboardButton(
            text="<-",
            callback_data=cb_factory(action=ACTION_PAGE, payload=current_page - 1).pack()
        ))
    footer_buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{page_count}",
        callback_data=cb_factory(action=ACTION_EMPTY, payload=0).pack()
    ))
    if current_page < page_count:
        footer_buttons.append(InlineKeyboardButton(
            text="->",
            callback_data=cb_factory(action=ACTION_PAGE, payload=current_page + 1).pack()
        ))

    keyborad_builder.row(*footer_buttons)
    return keyborad_builder.as_markup()
