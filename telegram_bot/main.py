import asyncio
from tbot_app import bot, dp
from tbot_app.handlers import summary, saving, history


async def main():
    dp.include_routers(summary.router, history.router, saving.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
