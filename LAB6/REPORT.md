# Лабораторна робота 6: DevOps, CI/CD, Docker
### Flask Task Manager API — Демо-звіт

---

## 1. Опис проєкту

**Task Manager API** — REST-сервіс для керування задачами, побудований на:

| Компонент | Технологія |
|---|---|
| Мова / фреймворк | Python 3.12 + Flask 3.0 |
| База даних | MongoDB 7.0 |
| Контейнеризація | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Тестування | pytest + mongomock (15 тестів, 93% coverage) |
| Лінтер | flake8 |

---

## 2. Архітектура сервісу

```
┌──────────────────────────────────────────────────────┐
│                   docker-compose.yaml                │
│                                                      │
│  ┌─────────────────┐       ┌──────────────────────┐  │
│  │   flask_app     │──────▶│      mongo:27017     │  │
│  │  (port 5000)    │       │  (volume: mongo_data)│  │
│  └─────────────────┘       └──────────────────────┘  │
│                                                      │
│  ┌─────────────────┐                                 │
│  │  tests (profile │  ← запускається вручну          │
│  │   "testing")    │    docker compose run tests     │
│  └─────────────────┘                                 │
└──────────────────────────────────────────────────────┘
```

---

## 3. API Endpoints

| Метод | URL | Опис | HTTP-статус |
|---|---|---|---|
| GET | `/health` | Перевірка стану | 200 |
| GET | `/tasks` | Список задач | 200 |
| POST | `/tasks` | Створити задачу | 201 |
| GET | `/tasks/:id` | Отримати задачу | 200 / 404 |
| PUT | `/tasks/:id` | Оновити задачу | 200 / 404 |
| DELETE | `/tasks/:id` | Видалити задачу | 200 / 404 |

---

## 4. Dockerfile (Multi-stage)

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

FROM base AS production        # docker compose up
ENV FLASK_DEBUG=false
EXPOSE 5000
CMD ["python", "app.py"]

FROM base AS test              # docker compose run tests
CMD ["pytest", "tests/", "-v", "--cov=app"]
```

**Переваги Multi-stage:**
- Production-образ не містить тестових залежностей
- Один `Dockerfile` для двох сценаріїв
- Кешування шарів (`COPY requirements.txt` окремо від коду)

---

## 5. Docker Compose

```yaml
services:
  mongo:      # MongoDB з healthcheck
  app:        # Flask (залежить від mongo: healthy)
  tests:      # Pytest (profile: testing — не стартує автоматично)
```

Запуск:
```bash
docker compose up --build           # запустити app + mongo
docker compose run --rm tests       # запустити тести
```

---

## 6. CI/CD Pipeline (GitHub Actions)

```
┌─────────────┐    ✅    ┌──────────────────┐    ✅    ┌─────────────────┐
│  🔍 Lint    │─────────▶│ 🧪 Tests+Coverage│─────────▶│ 🐳 Docker Build │
│  (flake8)   │         │   (pytest, 93%)  │         │   → Push GHCR*  │
└─────────────┘         └──────────────────┘         └─────────────────┘
                                                       * тільки main branch
```

Файл: `.github/workflows/ci.yml`

**Кроки pipeline:**
1. **Lint** — `flake8 app.py tests/ --max-line-length=100`
2. **Test** — `pytest tests/ -v --cov=app --cov-report=xml`
3. **Build** — `docker/build-push-action` (target: production)
4. **Push** — публікація до `ghcr.io` при merge до `main`

---

## 7. Результати тестування

```
tests/test_app.py::test_health                     PASSED
tests/test_app.py::test_get_tasks_empty            PASSED
tests/test_app.py::test_get_tasks_after_create     PASSED
tests/test_app.py::test_create_task_success        PASSED
tests/test_app.py::test_create_task_missing_title  PASSED
tests/test_app.py::test_create_task_no_body        PASSED
tests/test_app.py::test_get_task_by_id             PASSED
tests/test_app.py::test_get_task_not_found         PASSED
tests/test_app.py::test_get_task_invalid_id        PASSED
tests/test_app.py::test_update_task                PASSED
tests/test_app.py::test_update_task_not_found      PASSED
tests/test_app.py::test_update_task_no_valid_fields PASSED
tests/test_app.py::test_delete_task                PASSED
tests/test_app.py::test_delete_task_not_found      PASSED
tests/test_app.py::test_delete_task_invalid_id     PASSED

Name     Stmts   Miss  Cover
----------------------------
app.py      71      5    93%

15 passed in 1.69s
```

---

## 8. Структура файлів

```
flask-mongo-app/
├── app.py                  ← Flask REST API (71 рядок)
├── requirements.txt        ← flask, pymongo, pytest, mongomock, flake8
├── Dockerfile              ← Multi-stage (base / production / test)
├── docker-compose.yaml     ← mongo + app + tests
├── .env.example            ← шаблон змінних середовища
├── .gitignore
├── README.md               ← документація
├── tests/
│   └── test_app.py         ← 15 unit-тестів
└── .github/
    └── workflows/
        └── ci.yml          ← GitHub Actions pipeline
```

---

## 9. Приклад роботи API

```bash
# Запустити
docker compose up --build

# Перевірити здоров'я
curl http://localhost:5000/health
# {"status": "ok", "timestamp": "2024-01-15T10:30:00"}

# Створити задачу
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Здати лабораторну", "description": "Flask + Docker + CI/CD"}'
# {"_id": "664a1b...", "title": "Здати лабораторну", "done": false, ...}

# Отримати всі задачі
curl http://localhost:5000/tasks
# [{"_id": "664a1b...", "title": "Здати лабораторну", "done": false}]

# Позначити як виконану
curl -X PUT http://localhost:5000/tasks/664a1b... \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

---

*Лабораторна робота 6 — DevOps, CI/CD, Docker | Python / Flask / MongoDB*
