import os
from celery import Celery

from chat_manager import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_manager.settings')

import django
django.setup()

celery_app = Celery("chat_manager")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# celery_app.conf.update(
#     imports=("manager_app.tasks",)
# )

@celery_app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
