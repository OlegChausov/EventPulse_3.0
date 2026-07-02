#!/bin/sh
set -e

echo "⏳ Ожидание инициализации PostgreSQL..."
sleep 3

echo "🚀 Запуск автоматических миграций Alembic..."
alembic upgrade head

echo "✅ Миграции применены! Передаем управление серверу..."
exec "$@"