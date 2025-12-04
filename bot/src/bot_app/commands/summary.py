from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientSession
from magic_filter import F

from bot_app.api.api import summarize
from bot_app.api.subscriptions import get_user_groups
from bot_app.commands.groups_kb import create_kb, ACTION_EMPTY, ACTION_PAGE

router = Router()


class SummaryCBDataFactory(CallbackData, prefix='summary'):
    action: str
    payload: int


ACTION_SUMMARY = "summary"


@router.message(Command(commands="summary"))
async def summary_cmd_start(message: Message, aiohttp_session: ClientSession):
    groups = await get_user_groups(aiohttp_session, message.from_user.id)
    markup = create_kb(groups, ACTION_SUMMARY, SummaryCBDataFactory)
    await message.answer("Выберите группу", reply_markup=markup)


@router.callback_query(SummaryCBDataFactory.filter(F.action == ACTION_SUMMARY))
async def group_summary(callback: CallbackQuery, callback_data: SummaryCBDataFactory, aiohttp_session: ClientSession):
    group_id = callback_data.payload
    await callback.answer()
    await callback.message.edit_text(f"Готовим саммари для {group_id}. Результат пришлём новым сообщением")
    summary = await summarize(aiohttp_session, group_id)
    await callback.message.answer(summary)
    await callback.message.delete()


@router.callback_query(SummaryCBDataFactory.filter(F.action == ACTION_PAGE))
async def summary_page_cb(callback: CallbackQuery, callback_data: SummaryCBDataFactory, aiohttp_session: ClientSession):
    groups = await get_user_groups(aiohttp_session, callback.message.from_user.id)
    markup = create_kb(groups, ACTION_SUMMARY, SummaryCBDataFactory, current_page=callback_data.payload)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer(callback.data)


@router.callback_query(SummaryCBDataFactory.filter(F.action == ACTION_EMPTY))
async def summary_nop_cb(callback: CallbackQuery):
    await callback.answer()
