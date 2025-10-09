import asyncio
import os

import aiohttp
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from bot.src.bot_app.routers import main_subrouter
from bot.src.bot_app.commands import draft, search, stats, summary

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher()

dispatcher.include_routers(
    draft.router,
    search.router,
    stats.router,
    summary.router,
    main_subrouter.router
)


async def main():
    commands = [
        BotCommand(command="summary", description="Get message summary"),
        BotCommand(command="stats", description="Message stats"),
        BotCommand(command="draft", description="Draft answer"),
        BotCommand(command="search", description="Search by keywords"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    async with aiohttp.ClientSession() as aiohttp_session:
        dispatcher["aiohttp_session"] = aiohttp_session
        await dispatcher.start_polling(bot, polling_timeout=60)


if __name__ == '__main__':
    asyncio.run(main())
