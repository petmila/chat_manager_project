# from manager_app import models, serializers
# from llm_models.text_preprocess import preprocess
# from rest_framework.exceptions import ValidationError
# import pika
# import json
# from celery import celery_app
# import logging
#
# RABBITMQ_HOST = "rabbitmq"
# logger = logging.getLogger(__name__)
#
# @celery_app.task(bind=True, queue="updates_queue")
# def consume_messages(self):
#     """Фоновая задача для обработки сообщений из RabbitMQ"""
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
#     channel = connection.channel()
#     channel.queue_declare(queue="updates_queue", durable=True)
#
#     def callback(ch, method, body):
#         """Обрабатывает входящие сообщения"""
#         data = json.loads(body)
#         save_message(data)
#         ch.basic_ack(delivery_tag=method.delivery_tag)
#
#     channel.basic_consume(queue="updates_queue", on_message_callback=callback)
#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         channel.stop_consuming()
#     finally:
#         connection.close()
#
#
# def save_message(data) -> bool:
#     print(data)
#     print(f"📩 Сохранение сообщения от {data}")  # Выведет в Celery logs
#     logger.info(f"📩 Лог сообщения от {data}")  # Выведет в Django logs
#     return True
#     # is_employee_in_this_chat: bool = False
#     # account = models.EmployeeAccount.objects.filter(nickname=data['forward_from']).first()
#     # # message is forwarded
#     # if account is not None:
#     #     messages = models.Message.objects.filter(employee_account=account).order_by('timestamp')
#     #     for message in messages:
#     #         if str(message.chat.source_chat_id) == str(data['chat']['source_chat_id']):
#     #             is_employee_in_this_chat = True
#     #     if is_employee_in_this_chat:
#     #         data['employee_account']['nickname'] = data['forward_from']
#     #     else:
#     #         data['text'] = 'согласно словам ' + data['forward_from'] + ' ' + data['text']
#     # data['text'] = preprocess(data['text'])
#     # serializer = serializers.MessageSerializer(data=data)
#     # try:
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     # except ValidationError:
#     #     return False
#     # else:
#     #     return True
