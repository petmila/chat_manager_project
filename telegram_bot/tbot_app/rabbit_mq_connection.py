
import pika
import json


class RabbitMQConnection:
    def __init__(self, host="rabbitmq"):
        self.host = host
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Создаёт соединение"""
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, heartbeat=600))
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()

    def _ensure_connection(self):
        """Переподключение при закрытом соединении"""
        if not self.connection or self.connection.is_closed:
            self.connect()

    def send_message(self, queue_name, message):
        """Отправляет сообщение в очередь"""
        self._ensure_connection()
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message, default=str),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def close(self):
        """Закрывает соединение"""
        if self.connection and self.connection.is_open:
            self.connection.close()
