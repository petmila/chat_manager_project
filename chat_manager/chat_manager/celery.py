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
#     # # Calls test('hello') every 10 seconds.
#     # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

#     # # Calls test('hello') every 30 seconds.
#     # # It uses the same signature of previous task, an explicit name is
#     # # defined to avoid this task replacing the previous one defined.
#     # sender.add_periodic_task(30.0, test.s('hello'), name='add every 30')

#     # sender.add_periodic_task(60.0, save.s('nice ass'), expires=10)

@celery_app.task
def save(text):
    from manager_app import models
    obj_ = models.ModelResponseStrategy(strategy_name=text)
    obj_.save()

@celery_app.task
def perform_summary_on_chat(*args, **kwargs):
    """
    source_chat_id: чат, в который нужно прислать результат
    content_chat:   чат из которого генерируется резюме
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
    first_date = datetime.datetime.today() - datetime.timedelta(days=1)
    last_date = datetime.datetime.today() + datetime.timedelta(days=1)
    
    chat = models.Chat.objects.filter(id=int(content_chat)).first()
    messages = models.Message.objects.filter(chat=chat,
                                             timestamp__range=(first_date, last_date)).order_by('timestamp')
    # TODO: source_chat_id
    data = perform_summary(messages)
    serializer = serializers.ModelResponseSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
    except ValidationError:
        data['text'] = "В системе отсутствуют сообщения за указанный период времени"
    send_to_bot_via_queue(data)

celery_app.conf.update(
    imports=("chat_manager.celery",)
)
