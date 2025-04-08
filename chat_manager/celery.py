# import os
# from celery import Celery
# from celery.signals import worker_ready
# from manager_app.tasks import consume_messages
#
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_manager.settings")
#
# celery_app = Celery("chat_manager")
# celery_app.config_from_object("django.conf:settings", namespace="CELERY")
#
# celery_app.autodiscover_tasks()
#
#
# @worker_ready.connect
# def start_consumer(sender, **kwargs):
#     """Запускает Consumer автоматически при старте Celery"""
#     consume_messages.delay()
#
# #