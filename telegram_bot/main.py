import asyncio
from tbot_app import bot, dp, session
from tbot_app.handlers import summary, saving, history, private


async def main():
    dp.include_routers(private.router, summary.router, history.router, saving.router)
    session.start()
    await dp.start_polling(bot, close_bot_session=True)

if __name__ == "__main__":
    asyncio.run(main())
