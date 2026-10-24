# Микросервис Службы Международной Доставки

Асинхронный бэкенд для регистрации посылок, автоматического расчёта стоимости
доставки и умной техподдержки (RAG), а также веб-интерфейс на React.

## Технологический стек

**Бэкенд:** Python 3.12, FastAPI, SQLAlchemy (async), Pydantic v2, Alembic
**Базы данных:** PostgreSQL (данные), Qdrant (векторный поиск для ИИ), SQLite (тесты)
**Фоновые задачи и кэш:** Celery, Celery Beat, Redis
**Фронтенд:** React 18, TypeScript, Vite, TanStack Query, React Router, Tailwind CSS
**Инфраструктура:** Docker, Docker Compose

## Что умеет сервис

- Регистрация посылки: название, вес, стоимость содержимого, тип.
- Проверка бизнес-правил на входе (вес до 31,5 кг, положительные значения).
- Автоматический расчёт стоимости доставки в рублях по курсу ЦБ (раз в 5 минут).
- Список своих посылок с фильтрами, пагинацией и сортировкой по дате.
- Карточка посылки, пересчёт стоимости по кнопке и удаление.
- ИИ-поддержка: ответы по правилам доставки из `knowledge_base.txt` (RAG + LLM).
- Веб-интерфейс для всего перечисленного.

## Как устроен проект (ключевые особенности)

1. **Сессии без авторизации.** У каждого анонимного пользователя свой
   `session_id` в httponly-куке, поэтому посылки изолированы по браузерам.
   Кука живёт год, чтобы список не пропадал после перезапуска браузера.
2. **Фоновый расчёт.** Celery Beat раз в 5 минут запускает задачу: она берёт курс
   USD (Redis-кеш → API ЦБ → последнее сохранённое значение), после чего считает
   стоимость всех необработанных посылок. Задача повторяется при сбоях
   (`autoretry` до 3 раз).
3. **Умный помощник (RAG + диалог).** `knowledge_base.txt` делится на чанки,
   векторизуется через FastEmbed и складывается в Qdrant. По вопросу пользователя
   находятся три ближайших чанка и передаются в LLM OpenRouter как справка о
   правилах компании. Ассистент при этом не ограничен темой доставки: он
   поддерживает обычный разговор и отвечает на любые вопросы, а история последних
   реплик отправляется вместе с запросом, чтобы он понимал продолжение диалога.
4. **Фронтенд.** SPA на React: в dev-режиме Vite проксирует API на FastAPI,
   в проде собранная статика отдаётся тем же FastAPI из `/app/static`, поэтому
   куки остаются same-origin и CORS не нужен.

---

## Быстрый запуск (Docker Compose)

### 1. Подготовка окружения

Создайте `.env` на основе `.env.example`. Для запуска в Docker важны хосты
внутри сети compose:

```env
APP_TITLE="Shipping Service"
ENVIRONMENT=development
DEBUG=true
PORT=8000

DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=secret_password
DB_NAME=shipping_db

REDIS_HOST=redis
REDIS_PORT=6379

QDRANT_HOST=qdrant
QDRANT_PORT=6333

OPENROUTER_API_KEY=ваш_ключ_openrouter
```

### 2. Сборка и запуск

```bash
docker compose build
docker compose up -d
```

`web` собирается в два этапа: сначала `frontend/dist` (Node 20), затем
Python-образ, куда эта сборка копируется в `/app/static`.

### 3. Миграции базы данных

```bash
docker compose run --rm web alembic upgrade head
```

Базовые типы посылок и векторная база знаний индексируются автоматически при
старте сервера (lifespan-обработчик).

### 4. Открыть

- **Веб-интерфейс:** http://localhost:8080
- **Swagger:** http://localhost:8080/docs
- **Healthcheck:** http://localhost:8080/healthcheck

---

## Веб-интерфейс

| Экран | Что делает |
|---|---|
| `/parcels` | Список посылок: фильтры по типу и статусу расчёта, пагинация, удаление, кнопка «Пересчитать всё» |
| `/parcels/new` | Форма регистрации посылки с клиентской и серверной валидацией |
| `/parcels/:id` | Карточка: стоимость доставки, детали, пересчёт, удаление |
| `/support` | Чат с ИИ-ассистентом и готовые вопросы-подсказки |

### Разработка фронтенда

```bash
cd frontend
npm ci
npm run dev     # http://localhost:5173, API проксируется на localhost:8080
npm run build   # production-сборка в frontend/dist
```

Vite проксирует `/api` и `/healthcheck` на бэкенд, поэтому кука сессии
передаётся без настройки CORS. Если фронтенд запускается на отдельном origin,
задайте `CORS_ORIGINS=["http://localhost:5173"]`.

Все API-эндпоинты живут под префиксом `/api`, чтобы клиентские маршруты SPA
(`/parcels`, `/support`) не конфликтовали с API при прямом заходе по ссылке.

После изменений фронтенда пересоберите контейнер:

```bash
docker compose up -d --build web
```

В `docker-compose.yml` у `web` и Celery смонтированы только `./src` и
`knowledge_base.txt` — собранная статика берётся из образа и не затирается
bind-mount'ом.

---

## API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/types` | Типы посылок |
| `POST` | `/api/parcels` | Создать посылку → `201` + объект |
| `GET` | `/api/parcels` | Список с пагинацией и фильтрами |
| `GET` | `/api/parcels/{id}` | Посылка текущей сессии |
| `DELETE` | `/api/parcels/{id}` | Удалить посылку → `204` |
| `POST` | `/api/parcels/{id}/recalculate` | Сбросить стоимость и поставить пересчёт в очередь → `202` |
| `POST` | `/api/parcels/calculate-now` | Пересчитать все необработанные посылки |
| `POST` | `/api/support/ask` | Вопрос ИИ-поддержке |
| `GET` | `/healthcheck` | Проверка PostgreSQL, Redis и Qdrant |

`POST /api/support/ask` принимает `question` и необязательную `history` — массив
предыдущих сообщений `{"role": "user" | "assistant", "content": "..."}` (до 20
штук). Без истории ассистент ответит на одиночный вопрос, с историей — продолжит
разговор и поймет отсылки вроде «а почему?».

### Пагинация и фильтры

```http
GET /api/parcels?limit=10&offset=0&type_id=2&is_calculated=false
```

```json
{
  "items": [
    {
      "id": "2aa26bf2-e8e8-4048-9f0d-41bde318270e",
      "name": "Планшет",
      "weight": 0.8,
      "content_value": 350.0,
      "type_id": 2,
      "type_name": "Электроника",
      "carrier_name": null,
      "delivery_cost": null,
      "created_at": "2026-10-24T06:30:46.833334Z",
      "is_calculated": false
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

Стоимость приходит числом или `null` (а не строкой «Не рассчитано»), статус
расчёта — отдельным полем `is_calculated`.

### Формат ошибок

```json
{
  "status": "error",
  "message": "Переданы некорректные данные",
  "details": [
    {
      "type": "less_than_equal",
      "loc": ["body", "weight"],
      "msg": "Input should be less than or equal to 31.5"
    }
  ]
}
```

### Пример работы через curl

```bash
# Создать посылку (кука сессии сохраняется в cookie.jar)
curl -c cookie.jar -X POST http://localhost:8080/api/parcels \
  -H "Content-Type: application/json" \
  -d '{"name":"Планшет","weight":0.8,"content_value":350,"type_id":2}'

# Список своих посылок
curl -b cookie.jar "http://localhost:8080/api/parcels?limit=10"

# Вопрос поддержке (history необязательна, но нужна для продолжения диалога)
curl -b cookie.jar -X POST http://localhost:8080/api/support/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Можно ли отправить ноутбук?","history":[]}'
```

---

## Тестирование и покрытие

Тесты: интеграционные (API через `httpx.AsyncClient`) и юнит-тесты сервисов.
Текущее покрытие — **75%**.

```bash
docker compose up -d
docker compose run --rm web pytest --cov=src --cov-report=term-missing
```

Qdrant должен быть доступен из контейнера `web`, поэтому тесты запускаются
внутри Docker (тестовая БД — SQLite in-memory, LLM замокан).

### Статический анализ

```bash
source .venv/bin/activate
ruff check
mypy src
```

---

## Структура проекта

```
src/
├── main.py              # приложение, обработчики ошибок, healthcheck, статика
├── config.py            # настройки из .env
├── database.py          # async-движок SQLAlchemy
├── seed.py              # базовые типы посылок
├── worker.py            # Celery Beat + задача расчёта
├── middlewares/session.py
├── models/              # Parcel, ParcelType
├── schemas/             # валидация запросов/ответов
├── routers/             # parcels, types, support
└── services/            # currency, delivery, llm, rag
frontend/
├── src/api/             # клиент API и типы
├── src/components/      # Layout, таблица, форма, фильтры, пагинация
├── src/pages/           # 4 экрана
└── vite.config.ts       # dev-прокси на FastAPI
alembic/                 # миграции
tests/                   # pytest
```
