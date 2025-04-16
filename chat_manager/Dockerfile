FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD python manage.py migrate && python manage.py migrate django_celery_beat && python create_superuser.py && python manage.py runserver 0.0.0.0:8000
