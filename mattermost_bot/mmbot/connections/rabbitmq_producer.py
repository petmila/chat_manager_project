import aio_pika
import json


class RabbitMQConnection:
    def __init__(self, host="rabbitmq"):
        self.host = host
        self.connection = None
        self.channel = None

    async def connect(self):
        """Создаёт асинхронное соединение и канал"""
        self.connection = await aio_pika.connect_robust(f"amqp://{self.host}/")
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    async def _ensure_connection(self):
        """Переподключение при закрытом соединении"""
        if not self.connection or self.connection.is_closed:
            await self.connect()

    async def send_message(self, queue_name, message: dict):
        """Отправляет сообщение в очередь"""
        await self._ensure_connection()
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message, default=str).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue.name
        )

    async def close(self):
        """Закрывает соединение"""
        if self.connection:
            await self.connection.close()