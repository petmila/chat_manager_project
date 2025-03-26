import os
import django
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

User = get_user_model()

USERNAME = os.getenv("DJANGO_SUPERUSER_USERNAME")
EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL")
PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if hasattr(User.objects, "create_superuser"):
    if not User.objects.filter(username=USERNAME).exists():
        print(f"Создаём суперпользователя: {USERNAME}")
        User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    else:
        print("Суперпользователь уже существует.")
else:
    print("Ошибка: у User.objects нет метода create_superuser. Проверьте модель пользователя.")
