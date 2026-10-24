# ---------- Этап 1: сборка фронтенда ----------
FROM node:20-alpine AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---------- Этап 2: бэкенд ----------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Ставим утилиту curl (нужна для проверки здоровья Qdrant в docker-compose)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Собранный фронтенд FastAPI отдает из /app/static
COPY --from=frontend /frontend/dist ./static

EXPOSE 8000
