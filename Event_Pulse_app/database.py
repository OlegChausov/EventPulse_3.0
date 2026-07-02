import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .db_base import Base

# Загружаем переменные из .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Зависимость FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Временная инициализация таблиц — до Alembic
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
