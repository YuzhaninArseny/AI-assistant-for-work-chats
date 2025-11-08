# python -m apps.migrator
import os, sys, time
from pathlib import Path

import psycopg
from sqlalchemy import create_engine, text

from alembic import command
from alembic.config import Config

DB_URL = os.getenv("ALEMBIC_URL")


def wait_db(url: str, retries: int = 15, delay: float = 1.0):
    engine = create_engine(url, pool_pre_ping=True)
    for _ in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception:
            time.sleep(delay)
    sys.exit("DB is not reachable")


def main():
    if not DB_URL:
        print("DB_URL is not set", file=sys.stderr)
        sys.exit(1)

    wait_db(DB_URL)

    # ХАРДКОД- надо поменять потом
    cfg = Config("migrator/alembic.ini")


    command.upgrade(cfg, "head")
    print("\n===== CURRENT DB VERSION =====")
    command.current(cfg)

if __name__ == "__main__":
    main()
