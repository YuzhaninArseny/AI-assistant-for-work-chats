from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import ClientSession
from magic_filter import F

from bot_app.api.api import search
from bot_app.api.subscriptions import get_user_groups
from bot_app.commands.groups_kb import ACTION_PAGE, ACTION_EMPTY, create_kb, get_group_name

router = Router()

ACTION_SEARCH = "search"
ACTION_CANCEL_SEARCH = "cancel"


class SearchCBDataFactory(CallbackData, prefix='search'):
    action: str
    payload: int


class FSMAllStates(StatesGroup):
    basic = State()
    entering_search_query = State()


@router.message(Command(commands="search"))
async def search_cmd_start(message: Message, aiohttp_session: ClientSession, state: FSMContext):
    groups = await get_user_groups(aiohttp_session, message.from_user.id)
    markup = await create_kb(groups, ACTION_SEARCH, SearchCBDataFactory, state)
    await message.answer(f"Выберите группу, в которой искать", reply_markup=markup)


@router.callback_query(SearchCBDataFactory.filter(F.action == ACTION_SEARCH))
async def group_search_enter(callback: CallbackQuery, callback_data: SearchCBDataFactory, state: FSMContext):
    group_id = callback_data.payload
    await state.set_state(FSMAllStates.entering_search_query)
    await state.update_data(group_id=group_id)
    await state.update_data(prompt_msg_id=callback.message.message_id)
    group_name = get_group_name(group_id, await state.get_value("page_groups"))
    await callback.answer()

    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Отмена",
                             callback_data=SearchCBDataFactory(action=ACTION_CANCEL_SEARCH, payload=0).pack())
    ]])
    await callback.message.edit_text(f"Пришлите поисковый запрос для группы {group_name}", reply_markup=markup)


@router.message(StateFilter(FSMAllStates.entering_search_query))
async def group_search(message: Message, state: FSMContext, bot: Bot, aiohttp_session: ClientSession):
    group_id = await state.get_value("group_id")
    group_name = get_group_name(group_id, await state.get_value("page_groups"))
    prompt_msg_id = await state.get_value("prompt_msg_id")
    await state.clear()

    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=prompt_msg_id)
    sent = await message.answer(f"Выполняем поиск {group_name}. Результат пришлём новым сообщением")
    search_result = await search(aiohttp_session, group_id, message.text.split())
    await message.answer(search_result, parse_mode='markdown')
    await sent.delete()


@router.callback_query(SearchCBDataFactory.filter(F.action == ACTION_PAGE))
async def search_page_cb(callback: CallbackQuery, callback_data: SearchCBDataFactory,
                         aiohttp_session: ClientSession, state: FSMContext):
    groups = await get_user_groups(aiohttp_session, callback.message.from_user.id)
    markup = await create_kb(groups, ACTION_SEARCH, SearchCBDataFactory, state, current_page=callback_data.payload)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer(callback.data)


@router.callback_query(SearchCBDataFactory.filter(F.action == ACTION_EMPTY))
async def search_nop_cb(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(SearchCBDataFactory.filter(F.action == ACTION_CANCEL_SEARCH))
async def search_nop_cb(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
