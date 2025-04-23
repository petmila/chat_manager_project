import asyncio
import json

import pika

from tbot_app import bot


async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

def callback(ch, method, properties, body):
    data = json.loads(body)
    chat_id = data["chat_id"]
    text = data["text"]

    asyncio.run(send_message(chat_id, text))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consumer_start():
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="tg_bot_outbox", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="tg_bot_outbox", on_message_callback=callback)
    channel.start_consuming()