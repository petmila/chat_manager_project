FROM python:3.11

WORKDIR /bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y locales
RUN echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen
RUN update-locale LANG=ru_RU.UTF-8

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]