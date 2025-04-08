import asyncio
import signal
from tbot_app import bot, dp, connection, session
from tbot_app.handlers import summary, saving, history, private


async def shutdown():
    """Закрывает соединение при остановке бота"""
    connection.close()

async def main():
    dp.include_routers(private.router, summary.router, history.router, saving.router)
    session.start()
    try:
        await dp.start_polling(bot, close_bot_session=True)
    finally:
        await connection.close()
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
    #
    # loop = asyncio.get_event_loop()
    # for signame in ("SIGINT", "SIGTERM"):
    #     loop.add_signal_handler(getattr(signal, signame), lambda: asyncio.create_task(shutdown()))
    #
    # loop.run_until_complete(main())
