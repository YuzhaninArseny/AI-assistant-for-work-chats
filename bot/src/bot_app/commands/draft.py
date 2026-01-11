from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientSession
from magic_filter import F

from bot_app.api.api import draft
from bot_app.api.subscriptions import get_user_groups
from bot_app.commands.groups_kb import ACTION_PAGE, create_kb, ACTION_EMPTY, get_group_name

router = Router()

ACTION_DRAFT = "draft"


class DraftCBDataFactory(CallbackData, prefix='draft'):
    action: str
    payload: int


@router.message(Command(commands="draft"))
async def draft_cmd_start(message: Message, aiohttp_session: ClientSession, state: FSMContext):
    groups = await get_user_groups(aiohttp_session, message.from_user.id)
    markup = await create_kb(groups, ACTION_DRAFT, DraftCBDataFactory, state)
    await message.answer(f"Выберите группу", reply_markup=markup)


@router.callback_query(DraftCBDataFactory.filter(F.action == ACTION_DRAFT))
async def group_search(callback: CallbackQuery, callback_data: DraftCBDataFactory,
                       aiohttp_session: ClientSession, state: FSMContext):
    group_id = callback_data.payload
    group_name = get_group_name(group_id, await state.get_value("page_groups"))
    await state.clear()

    await callback.answer()
    await callback.message.edit_text(f"Генерируем ответ для {group_name}. Результат пришлём новым сообщением")
    draft_ = await draft(aiohttp_session, group_id)
    await callback.message.answer(draft_)
    await callback.message.delete()


@router.callback_query(DraftCBDataFactory.filter(F.action == ACTION_PAGE))
async def draft_page_cb(callback: CallbackQuery, callback_data: DraftCBDataFactory,
                        aiohttp_session: ClientSession, state: FSMContext):
    groups = await get_user_groups(aiohttp_session, callback.message.from_user.id)
    markup = await create_kb(groups, ACTION_DRAFT, DraftCBDataFactory, state, current_page=callback_data.payload)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer(callback.data)


@router.callback_query(DraftCBDataFactory.filter(F.action == ACTION_EMPTY))
async def draft_nop_cb(callback: CallbackQuery):
    await callback.answer()
