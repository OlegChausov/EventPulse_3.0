from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool
import os
import sys
from dotenv import load_dotenv

# 1. Загружаем alembic.ini
config = context.config

# 2. Логирование
fileConfig(config.config_file_name)

# 3. Загружаем .env из корня проекта
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 4. Добавляем путь к приложению
sys.path.append(BASE_DIR)

# 5. Импортируем модели
from Event_Pulse_app.db_base import Base
from Event_Pulse_app import models

target_metadata = Base.metadata

# 6. Формируем URL из .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Если запущено внутри Docker-контейнера — хост всегда 'db' (имя сервиса в compose).
# Если запущено локально на хосте (например для autogenerate без Docker) — берём DB_HOST из .env.
if os.path.exists("/.dockerenv"):
    DB_HOST = "db"
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()