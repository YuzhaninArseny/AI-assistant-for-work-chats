import asyncio
import logging
import os
import traceback

import aiohttp
from aiogram import Dispatcher, Bot, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, Message

from bot_app.commands import draft, search, stats, summary, groups
from bot_app.routers import main_subrouter

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(storage=MemoryStorage())

dispatcher.include_routers(
    draft.router,
    search.router,
    stats.router,
    summary.router,
    groups.router,

    main_subrouter.router
)


@dispatcher.errors(F.update.message.as_("message"))
async def on_error(event: types.ErrorEvent, message: Message):
    traceback.print_exception(event.exception)
    await message.answer("Произошла ошибка")


async def main():
    commands = [
        BotCommand(command="summary", description="Get message summary"),
        BotCommand(command="stats", description="Message stats"),
        BotCommand(command="draft", description="Draft answer"),
        BotCommand(command="search", description="Search by keywords"),
        BotCommand(command="groups", description="View my groups"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    async with aiohttp.ClientSession() as aiohttp_session:
        dispatcher["aiohttp_session"] = aiohttp_session
        logging.info("Bot ready")
        await dispatcher.start_polling(bot, polling_timeout=60)


logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    asyncio.run(main())
