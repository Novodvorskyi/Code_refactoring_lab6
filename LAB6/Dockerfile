
FROM python:3.12-slim AS base

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


FROM base AS production

ENV FLASK_DEBUG=false \
    PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]


FROM base AS test

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

CMD ["pytest", "tests/", "-v", "--cov=app", "--cov-report=term-missing"]
