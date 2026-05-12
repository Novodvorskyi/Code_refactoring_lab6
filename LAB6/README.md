# 📋 Flask Task Manager API

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/flask-mongo-app/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/flask-mongo-app/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)
![MongoDB](https://img.shields.io/badge/mongodb-7.0-green)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)

REST API для керування задачами, побудований на **Flask + MongoDB**, контейнеризований через **Docker**.

---

## 🚀 Запуск через Docker (рекомендований спосіб)

### 1. Клонувати репозиторій
```bash
git clone https://github.com/YOUR_USERNAME/flask-mongo-app.git
cd flask-mongo-app
```

### 2. Налаштувати змінні середовища
```bash
cp .env.example .env
# За потреби відредагуйте .env
```

### 3. Запустити сервіси
```bash
docker compose up --build
```

Додаток буде доступний на `http://localhost:5000`.

### 4. Запустити тести в Docker
```bash
docker compose run --rm tests
```

### 5. Зупинити сервіси
```bash
docker compose down          # зупинити контейнери
docker compose down -v       # зупинити + видалити volumes (дані MongoDB)
```

---

## 💻 Локальний запуск (без Docker)

### Вимоги
- Python 3.12+
- MongoDB 7.0 (локально або хмарна)

### Кроки
```bash
# 1. Створити та активувати virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Встановити залежності
pip install -r requirements.txt

# 3. Встановити змінні середовища
export MONGO_URI="mongodb://localhost:27017/"
export DB_NAME="taskdb"
export PORT=5000

# 4. Запустити додаток
python app.py
```

---

## 🔐 Змінні середовища

| Змінна | За замовчуванням | Опис |
|---|---|---|
| `MONGO_URI` | `mongodb://localhost:27017/` | URI підключення до MongoDB |
| `DB_NAME` | `taskdb` | Назва бази даних |
| `PORT` | `5000` | Порт Flask-сервера |
| `FLASK_DEBUG` | `false` | Режим налагодження (`true`/`false`) |
| `MONGO_USER` | `admin` | Ім'я користувача MongoDB (тільки в Docker) |
| `MONGO_PASSWORD` | `secret` | Пароль MongoDB (тільки в Docker) |

---

## 📡 API Endpoints

Base URL: `http://localhost:5000`

### Health Check

| Метод | Endpoint | Опис |
|---|---|---|
| `GET` | `/health` | Перевірка стану сервісу |

**Приклад відповіді:**
```json
{ "status": "ok", "timestamp": "2024-01-15T10:30:00.000Z" }
```

---

### Tasks (CRUD)

| Метод | Endpoint | Опис |
|---|---|---|
| `GET` | `/tasks` | Отримати всі задачі |
| `GET` | `/tasks/<id>` | Отримати задачу за ID |
| `POST` | `/tasks` | Створити нову задачу |
| `PUT` | `/tasks/<id>` | Оновити задачу |
| `DELETE` | `/tasks/<id>` | Видалити задачу |

**Структура задачі:**
```json
{
  "_id": "664a1b2c3d4e5f6789abcdef",
  "title": "Купити молоко",
  "description": "2% жирності",
  "done": false,
  "created_at": "2024-01-15T10:00:00.000Z"
}
```

**Приклади запитів (curl):**

```bash
# Отримати всі задачі
curl http://localhost:5000/tasks

# Створити задачу
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Зробити лабораторну", "description": "Flask + Docker"}'

# Оновити задачу
curl -X PUT http://localhost:5000/tasks/<ID> \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# Видалити задачу
curl -X DELETE http://localhost:5000/tasks/<ID>
```

---

## 🧪 Тести

### Запуск тестів локально
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Запуск тестів у Docker
```bash
docker compose run --rm tests
```

### Очікуваний результат
```
tests/test_app.py::test_health                    PASSED
tests/test_app.py::test_get_tasks_empty           PASSED
tests/test_app.py::test_create_task_success       PASSED
... (всього 15 тестів)

----------- coverage -----------
Name     Stmts   Miss  Cover
-----------------------------
app.py      71      5    93%

15 passed in 1.69s
```

Тести використовують **mongomock** — реальна MongoDB не потрібна для тестування.

### Що тестується:
- ✅ Health endpoint
- ✅ GET /tasks (порожній список та після створення)
- ✅ POST /tasks (успішно, без title, без тіла)
- ✅ GET /tasks/:id (знайдено, не знайдено, невалідний ID)
- ✅ PUT /tasks/:id (оновлення, не знайдено, невалідні поля)
- ✅ DELETE /tasks/:id (видалення, не знайдено, невалідний ID)

---

## ✅ Перевірка коректної роботи

### Через браузер
Відкрийте `http://localhost:5000/tasks` — має повернутись `[]` або список задач.

### Через Postman
1. Імпортуйте колекцію або створіть запит вручну
2. `GET http://localhost:5000/health` → `{"status": "ok"}`
3. `POST http://localhost:5000/tasks` з тілом `{"title": "Test"}` → задача з `_id`

---

## 🏗️ Структура проєкту

```
flask-mongo-app/
├── app.py                    # Flask додаток
├── requirements.txt          # Python залежності
├── Dockerfile                # Multi-stage Dockerfile
├── docker-compose.yaml       # App + MongoDB + Tests
├── .env.example              # Шаблон змінних середовища
├── .gitignore
├── tests/
│   └── test_app.py           # 15 unit-тестів
└── .github/
    └── workflows/
        └── ci.yml            # GitHub Actions CI/CD
```

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

Pipeline запускається при кожному `push` або `pull_request` до `main`/`develop`:

```
push/PR → [Lint] → [Tests + Coverage] → [Docker Build] → [Push to GHCR]*
                                                           * тільки для main
```

1. **🔍 Lint** — `flake8` перевірка стилю коду
2. **🧪 Tests** — `pytest` з coverage-звітом
3. **🐳 Docker Build** — збірка production-образу
4. **📦 Push to GHCR** — публікація образу (тільки гілка `main`)
