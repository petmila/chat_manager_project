# SummaryFromLlama

**`SummaryFromLlama`** — сервис генерации тезисов на основе анализа диалогов в корпоративных чатах в мессенджерах Mattermost и Telegram. Основная задача сервиса заключается в предоставлении сжатого и информативного изложения переписки, что способствует упрощению и ускорению внутренних коммуникационных процессов между сотрудниками компании.

## Стек технологий

* **Язык программирования:** Python 3.11
* **Фреймворк:** Django 5.2 + Django REST Framework
* **Асинхронные задачи:** Celery 5.5 + Rabbit
* **LLM:** `IlyaGusev/saiga_llama3_8b` (через LlamaCpp)
* **База данных:** PostgreSQL c расширением pgVector
* **Контейнеризация:** Docker + Docker Compose

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/petmila/chat_manager_project.git
cd chat_manager_project
```

### 2. Скачивание модели

Скачайте модель по ссылке и поместите `.gguf` файл в корневую директорию проекта

```bash
wget https://huggingface.co/IlyaGusev/saiga_llama3_8b_gguf/resolve/main/model-q4_K.gguf
```

### 3. Создание volume в docker для хранения .gguf файла llm

Создать docker-network
 
```bash
docker network create chat_network
```

Создать volume

```bash
docker volume create chat_manager_project_llm_model
```

Переместить в него `.gguf` файл

```bash
docker run --rm -v chat_manager_project_llm_model:/mnt -v chat_manager_project/ggml-model-Q4_K_M.gguf:/tmp/model-q4_K.gguf busybox sh -c "cp /tmp/model-q4_K.gguf /mnt/"
```

### 4. Настройка `.env` файлов

Поместите файлы `.env` в директории `/chat_manager`, `/telegram_bot` и `/mattermost_bot`

### 5. Сборка основного образа

```bash
docker build -t image_django_app ./chat_manager
```

### 5. Запуск контейнеров

```bash
docker-compose up --build
```

### 6. Документация

Перейдите в браузере по адресу, чтобы прочитать документацию к проекту:

```
http://localhost:8000/api/schema/swagger-ui/
http://localhost:8000/api/schema/redoc/
```

## Telegram-бот

### 1. Создание бота

Откройте Telegram и найдите `@BotFather`. Отправьте команду:

```
/newbot
```

Задайте:

* **Name** — отображаемое имя (например: `Summary From Llama`)
* **Username** — уникальное имя, заканчивающееся на `bot` (например: `summary_from_llama_bot`)

Скопируйте выданный токен.

### 2. Добавление токена в `.env`

```
TOKEN=123456789:ABCdefGhIJKlmnoPQRstuVWXyz
```
