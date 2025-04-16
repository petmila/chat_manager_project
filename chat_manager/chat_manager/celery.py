import os
from celery import Celery
from celery import shared_task
from chat_manager import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_manager.settings')

import django
django.setup()

celery_app = Celery("chat_manager")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    # # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # # Calls test('hello') every 30 seconds.
    # # It uses the same signature of previous task, an explicit name is
    # # defined to avoid this task replacing the previous one defined.
    # sender.add_periodic_task(30.0, test.s('hello'), name='add every 30')

    # # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    sender.add_periodic_task(60.0, save.s('nice ass'), expires=10)

@celery_app.task
def save(text):
    from manager_app import models
    obj_ = models.ModelResponseStrategy(strategy_name=text)
    obj_.save()

@celery_app.task
def test(arg):
    print(arg)

@celery_app.task
def add(x, y):
    z = x + y
    print(z)

celery_app.conf.update(
    imports=("chat_manager.celery",)
)
