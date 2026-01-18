from aiogram import Router
import logging
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientSession

from bot_app.api.subscriptions import get_user_groups, GroupInfo
from bot_app.commands.groups_kb import create_kb, ACTION_EMPTY, ACTION_PAGE, get_group_name
from bot_app.api.api import get_stats

router = Router()


class StatsCBDataFactory(CallbackData, prefix="stats"):
    action: str
    payload: int


ACTION_STATS = "stats"


def format_stats_report(chat_title: str, stats: dict) -> str:
    lines = [f"📈 **Статистика за последние 14 дней**\n\n📋 *Чат:* **{chat_title}**\n"]

    # === Топ-5 пользователей ===
    top_users = stats.get("top_users", [])
    if top_users:
        lines.append("🏆 **Топ активных участников:**")
        for i, user in enumerate(top_users[:5], 1):
            lines.append(f"{i}. ID `{user['user_id']}` — {user['message_count']} сообщений")
    else:
        lines.append("📭 Нет активности за последние 14 дней.")

    # === Активность по дням (последние 7 дней) ===
    lines.append("\n📆 **Активность по дням (последние 7 дней):**")
    daily = stats.get("daily_activity", {})

    # Сортируем дни по убыванию (свежие сверху)
    sorted_days = sorted(daily.items(), key=lambda x: x[0], reverse=True)

    shown_days = 0
    for day, activities in sorted_days:
        if shown_days >= 7:
            break
        total = sum(act["message_count"] for act in activities)
        if total > 0:
            lines.append(f"\n`{day}` — всего **{total}** сообщений")
            # Показываем топ-2 пользователя за день
            top_day = sorted(activities, key=lambda x: x["message_count"], reverse=True)[:2]
            for act in top_day:
                lines.append(f"  • ID `{act['user_id']}`: {act['message_count']}")
            shown_days += 1
        else:
            # Пропускаем пустые дни, чтобы не засорять
            continue

    if shown_days == 0 and top_users:
        lines.append("\nℹ️ Подробная активность по дням недоступна.")

    return "\n".join(lines)

@router.message(Command(commands=["stats"]))
async def stats_cmd_start(message: Message, aiohttp_session: ClientSession, state: FSMContext):
    groups = await get_user_groups(aiohttp_session, message.from_user.id)
    if not groups:
        await message.answer("У вас нет доступных чатов.")
        return
    markup = await create_kb(groups, ACTION_STATS, StatsCBDataFactory, state)
    await message.answer("📊 Выберите чат для просмотра статистики:", reply_markup=markup)


@router.callback_query(StatsCBDataFactory.filter(lambda c: c.action == ACTION_STATS))
async def stats_show(
    callback: CallbackQuery,
    callback_data: StatsCBDataFactory,
    aiohttp_session: ClientSession,
    state: FSMContext
):

    chat_id = callback_data.payload
    page_groups = (await state.get_data()).get("page_groups", [])
    group_name = get_group_name(chat_id, page_groups)
    await callback.answer()
    await callback.message.edit_text(f"📊 Готовим статистику для «{group_name}»...")

    try:
        stats = await get_stats(aiohttp_session, chat_id)
        report = format_stats_report(group_name, stats)
        await callback.message.answer(report, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error in stats_show: {e}")
        await callback.message.answer("❌ Не удалось получить статистику. Попробуйте позже.")
    finally:
        await callback.message.delete()
        await state.clear()


@router.callback_query(StatsCBDataFactory.filter(lambda c: c.action == ACTION_PAGE))
async def stats_page_cb(callback: CallbackQuery, callback_data: StatsCBDataFactory, aiohttp_session: ClientSession, state: FSMContext):
    groups = await get_user_groups(aiohttp_session, callback.from_user.id)
    markup = await create_kb(groups, ACTION_STATS, StatsCBDataFactory, state, current_page=callback_data.payload)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()


@router.callback_query(StatsCBDataFactory.filter(lambda c: c.action == ACTION_EMPTY))
async def stats_nop_cb(callback: CallbackQuery):
    await callback.answer()