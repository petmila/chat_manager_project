import asyncio
import json

import aio_pika

from tbot_app import bot


async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = message.body.decode()
        chat_id = data["chat_id"]
        text = data["text"]
        print(text)
        asyncio.run(send_message(chat_id, text))

async def start_async_consumer():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()
    queue = await channel.declare_queue("tg_bot_outbox", durable=True)
    await queue.consume(process_message)

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Consumer shutting down...")
        await connection.close()
        raise