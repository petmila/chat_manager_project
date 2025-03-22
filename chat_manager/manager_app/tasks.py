from celery import shared_task
import requests
from django.utils.timezone import now, timedelta
import django_celery_beat.models as celery_beat
import models
from .celery import app as app

TELEGRAM_BOT_URL = "http://127.0.0.1:8080/send_message"


@app.task(bind=True)
def summary_for_telegram_task(self, **kwargs):
    task_data = self.request.properties
    first_date = now() - timedelta(days=1)
    last_date = now()

    chat = models.Chat.objects.filter(chat_id=task_data['kwargs']['content_chat']).first()
    messages = models.Message.objects.filter(
        chat=chat,
        timestamp__range=(first_date, last_date)).order_by('timestamp')
    queryset = [str(message) for message in messages]
    print('-'.join(queryset))
    data = {
        "chat_id": chat.source_chat_id,
        "text": '-'.join(queryset)
    }
    if chat.chat_source == models.ChatSource.telegram:
        try:
            requests.post(TELEGRAM_BOT_URL, json=data, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке запроса в Telegram-бот: {e}")



# @shared_task
# def check_scheduled_tasks():
#     """
#     Проверяет запланированные задачи и отправляет их в ботов
#     """
#     tasks = models.TaskSchedule.objects.filter(next_run_time__lte=now())
#     for task in tasks:
#         first_date = now() - task.time_period_in_hours
#         last_date = now()
#         messages = models.Message.objects.filter(
#             chat=task.content_chat,
#             timestamp__range=(first_date, last_date)).order_by('timestamp')
#         queryset = [str(message) for message in messages]
#
#         print('-'.join(queryset))
#         data = {
#             "chat_id": task.source_chat_id,
#             "text": '-'.join(queryset)
#         }
#         if task.content_chat.chat_source == models.ChatSource.telegram:
#             try:
#                 requests.post(TELEGRAM_BOT_URL, json=data, timeout=5)
#             except requests.exceptions.RequestException as e:
#                 print(f"Ошибка при отправке запроса в Telegram-бот: {e}")
#
#         task.next_run_time += task.interval_hours
#         task.save()