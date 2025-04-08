import time

import pika
import json
from django.core.management.base import BaseCommand
import manager_app.models as models
import manager_app.serializers as serializers


class Command(BaseCommand):
    help = "Запускает RabbitMQ consumer для обработки сообщений"

    def handle(self, *args, **kwargs):
        def create_connection():
            while True:
                try:
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(
                            host='rabbitmq',
                            port=5672,
                            credentials=pika.PlainCredentials('guest', 'guest'),
                        )
                    )
                    return connection
                except pika.exceptions.AMQPConnectionError as e:
                    print(f"Ошибка подключения: {e}. Повторная попытка через 5 секунд...")
                    time.sleep(5)

        connection = create_connection()
        channel = connection.channel()
        channel.queue_declare(queue="updates_queue", durable=True)

        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)

                is_employee_in_this_chat: bool = False
                account = models.EmployeeAccount.objects.filter(nickname=data['forward_from']).first()
                # message is forwarded
                if account is not None:
                    messages = models.Message.objects.filter(employee_account=account).order_by('timestamp')
                    for message in messages:
                        if str(message.chat.source_chat_id) == str(data['chat']['source_chat_id']):
                            is_employee_in_this_chat = True
                    if is_employee_in_this_chat:
                        data['employee_account']['nickname'] = data['forward_from']
                    else:
                        data['text'] = 'согласно словам ' + data['forward_from'] + ' ' + data['text']
                # data['text'] = preprocess(data['text'])
                serializer = serializers.MessageSerializer(data=data)

                serializer.is_valid(raise_exception=True)
                serializer.save()
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume(queue="updates_queue", on_message_callback=callback)
        channel.start_consuming()
