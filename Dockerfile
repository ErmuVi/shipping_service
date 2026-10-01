# Используем официальный легкий образ Python
FROM python:3.12-slim

# Настраиваем переменные окружения для логов
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Настраиваем рабочую директорию внутри контейнера
WORKDIR /app

# Ставим утилиту curl (она нужна для проверки здоровья Qdrant в docker-compose)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей, который вы сгенерировали
COPY requirements.txt .

# Устанавливаем библиотеки напрямую через стандартный pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта в контейнер
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000
