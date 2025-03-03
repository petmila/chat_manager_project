import asyncio
from tbot_app import bot, dp, session
from tbot_app.handlers import summary, saving, history, private
from tbot_app.server import start_http_server


async def main():
    dp.include_routers(private.router, summary.router, history.router, saving.router)
    session.start()
    await dp.start_polling(bot, close_bot_session=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_http_server())
    asyncio.run(main())
