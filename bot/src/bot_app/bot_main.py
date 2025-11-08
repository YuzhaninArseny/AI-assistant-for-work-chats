import asyncio
import logging
import os

import aiohttp
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot_app.routers import main_subrouter
from bot_app.commands import draft, search, stats, summary, groups

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
        await dispatcher.start_polling(bot, polling_timeout=60)

logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    asyncio.run(main())
