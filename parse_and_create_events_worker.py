# parse_and_create_events_worker.py
import asyncio
import os
import sys
from sentence_transformers import SentenceTransformer

# Настройка политики для Windows, чтобы асинхронный event loop не сыпал ошибками закрытия сокетов
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Глобальное хранилище ИИ-модели внутри этого процесса. 
# Сюда будет стучаться умный импорт из fuzzy_match.py
worker_model_holder = {}

# Импортируем наш очищенный от FastAPI диспетчер с ежедневной очисткой кэша
from Event_Pulse_app.parser_loop import parser_loop



def _warmup_chromedriver() -> str | None:
    if sys.platform.startswith("win"):
        # Удаляем зависший лок-файл если есть
        lock_path = os.path.expanduser(r"~\.wdm\.wdm-lock-chromedriver-win64")
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print("🧹 Удалён зависший лок ChromeDriver", flush=True)
            except Exception as e:
                print(f"⚠️ Не удалось удалить лок: {e}", flush=True)

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            path = ChromeDriverManager().install()
            print(f"✅ ChromeDriver прогрет: {path}", flush=True)
            return path
        except Exception as e:
            import traceback
            print(f"⚠️ Прогрев ChromeDriver не удался: {e}", flush=True)
            traceback.print_exc()
    return None
    # На Linux — ничего не делаем, драйвер уже есть


def main():
    print("\n" + "="*50)
    print("🤖 [PARSE WORKER] Инициализация фонового цеха...")
    
    chromedriver_path = _warmup_chromedriver()
    if chromedriver_path:
        os.environ["CHROMEDRIVER_PATH"] = chromedriver_path
        print(f"🔧 CHROMEDRIVER_PATH установлен: {chromedriver_path}", flush=True)
    else:
        print("⚠️ CHROMEDRIVER_PATH не установлен!", flush=True)

    print("⏳ Загрузка ИИ-модели BAAI/bge-m3 в оперативную память...")
    try:
        # worker_model_holder["mini_lm"] = SentenceTransformer('BAAI/bge-m3')
        worker_model_holder["mini_lm"] = SentenceTransformer('./bge-m3-posters')
        print("✅ [PARSE WORKER] Модель успешно загружена и готова к мэтчингу!")
    except Exception as model_err:
        print(f"❌ [PARSE WORKER] Не удалось загрузить ИИ-модель: {model_err}")
        return

    print("🚀 [PARSE WORKER] Запуск изолированного цикла парсинга и ИИ-анализа...")
    print("="*50 + "\n")

    try:
        asyncio.run(parser_loop())
    except KeyboardInterrupt:
        print("\n🛑 [PARSE WORKER] Воркер остановлен вручную.")
    except Exception as e:
        print(f"❌ [PARSE WORKER] Критическая ошибка воркера: {e}")
    finally:
        print("🧹 [PARSE WORKER] Освобождение ресурсов и завершение процесса...")
        worker_model_holder.clear()

if __name__ == "__main__":
    main()