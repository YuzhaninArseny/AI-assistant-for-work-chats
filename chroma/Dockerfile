FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем ВСЕ файлы проекта
COPY . .

ENV PYTHONPATH=app/

# Устанавливаем зависимости
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--reload-dir", "/app"]