import pika
import json

def send_to_bot_via_queue(data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="tg_bot_outbox", durable=True)
    message = json.dumps(data)

    channel.basic_publish(
        exchange="",
        routing_key="tg_bot_outbox",
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )
    connection.close()
