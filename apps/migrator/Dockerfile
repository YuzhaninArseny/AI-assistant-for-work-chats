FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

RUN pip install --no-cache-dir alembic SQLAlchemy "psycopg[binary]"

COPY shared/src/shared ./shared
COPY migrator ./migrator

ENV PYTHONPATH=/app
ENTRYPOINT ["python", "-m", "migrator"]
CMD []
