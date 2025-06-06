import os
from celery import Celery
from celery import shared_task
from chat_manager import settings
import datetime


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_manager.settings')

import django
django.setup()

celery_app = Celery("chat_manager")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# @celery_app.on_after_configure.connect
# def snetup_periodic_tasks(seder: Celery, **kwargs):
#     # Calls test('hello') every 10 seconds.
#     sender.add_periodic_task(30.0, test.s('hello'), name='add every 30')

#     sender.add_periodic_task(60.0, save.s('nice ass'), expires=10)

@celery_app.task
def perform_summary_on_chat(*args, **kwargs):
    """
    kwargs:
        source_chat_id: чат, в который нужно прислать результат
        content_chat:   чат из которого генерируется резюме
        periodic_task_id: 
    """
    pt_id = kwargs.get('periodic_task_id')
    source_chat_id = kwargs.get('source_chat_id')
    content_chat = kwargs.get('content_chat')

    from manager_app import serializers, models
    from django_celery_beat.models import PeriodicTask
    from rest_framework.exceptions import ValidationError
    from utils.perform_summary import perform_summary
    from utils.rabbitmq_connection import send_to_bot_via_queue
    
    task = PeriodicTask.objects.get(id=pt_id)
    first_date = task.last_run_at
    if first_date is None:
        first_date = task.start_time
    last_date = datetime.datetime.now()
    
    chat = models.Chat.objects.filter(id=int(content_chat)).first()
    messages = models.Message.objects.filter(chat=chat,
                                             timestamp__range=(first_date, last_date)).order_by('timestamp')
    data = perform_summary(messages, chat_id=chat.id)
    serializer = serializers.ModelResponseSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
    except ValidationError:
        data['text'] = "В системе отсутствуют сообщения за указанный период времени"
    
    send_to_bot_via_queue(data, receiver_chat_id=source_chat_id)

celery_app.conf.update(
    imports=("chat_manager.celery",)
)
