# Event_Pulse_app/main.py
import asyncio
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from Event_Pulse_app.middleware.auth_middleware import JWTMiddleware
from Event_Pulse_app.middleware.set_lang_middleware import SetLangMiddleware
from Event_Pulse_app.middleware.token_expiration_moddleware import SlidingExpirationMiddleware

from Event_Pulse_app.routers import all_routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Теперь здесь идеальная чистота. Никаких тяжелых моделей и фоновых циклов!
    print("🚀 [FastAPI] Веб-сервер успешно запущен на Windows и готов обрабатывать роуты!")
    yield
    print("🛑 [FastAPI] Веб-сервер останавливается...")

# Настройка политики для Windows, чтобы не было ошибок с закрытием соединений
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Инициализируем приложение строго с чистым lifespan
app = FastAPI(lifespan=lifespan)

# Подключаем middleware
app.add_middleware(JWTMiddleware)
app.add_middleware(SlidingExpirationMiddleware)
app.add_middleware(SetLangMiddleware)

# Монтируем статику (динамический путь)
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Подключаем все роутеры из системы
for r in all_routers:
    app.include_router(r)