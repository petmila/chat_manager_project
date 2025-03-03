import requests
from celery import shared_task
from django.utils.timezone import now, timedelta
import models

TELEGRAM_BOT_URL = "http://127.0.0.1:8080/send_message"

@shared_task
def check_scheduled_tasks():
    """
    Проверяет запланированные задачи и отправляет их в ботов
    """
    tasks = models.TaskSchedule.objects.filter(next_run_time__lte=now())
    for task in tasks:
        first_date = now() - task.time_period_in_hours
        last_date = now()
        messages = models.Message.objects.filter(
            chat=task.content_chat,
            timestamp__range=(first_date, last_date)).order_by('timestamp')
        queryset = [str(message) for message in messages]

        print('-'.join(queryset))
        data = {
            "chat_id": task.source_chat_id,
            "text": '-'.join(queryset)
        }
        if task.content_chat.chat_source == models.ChatSource.telegram:
            try:
                requests.post(TELEGRAM_BOT_URL, json=data, timeout=5)
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при отправке запроса в Telegram-бот: {e}")

        task.next_run_time += task.interval_hours
        task.save()