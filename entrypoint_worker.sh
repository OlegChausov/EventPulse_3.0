#!/bin/sh
set -e

echo "⏳ [WORKER] Ожидание готовности API..."
sleep 10

echo "🚀 [WORKER] Запуск воркера парсинга..."
exec "$@"