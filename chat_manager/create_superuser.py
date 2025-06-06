import os
import django
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

import sys
print("=== Запуск create_superuser.py ===")
sys.stdout.flush()  # Принудительный вывод

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_manager.settings")
django.setup()

User = get_user_model()

USERNAME = os.getenv("TELEGRAM_ADMIN_USER")
EMAIL = os.getenv("TELEGRAM_ADMIN_EMAIL")
PASSWORD = os.getenv("TELEGRAM_ADMIN_PASSWORD")


if not User.objects.filter(username=USERNAME).exists():
    print(f"Создаём суперпользователя: {USERNAME}")
    User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
else:
    print("Суперпользователь уже существует.")

