# Event_Pulse_app/utils/fuzzy_match.py
import sys
import os
from functools import lru_cache
from Event_Pulse_app.models import EventQuery
from sentence_transformers import util

os.makedirs("logs", exist_ok=True)

# =====================================================================
# УРОВЕНЬ 1: КЭШ ЭМБЕДДИНГОВ СТРОК
# =====================================================================
@lru_cache(maxsize=1024)
def get_cached_embedding(text: str):
    """Считает вектор ТОЛЬКО если строки нет в кэше. Без лишних оберток."""
    model = None

    # Ищем модель в глобальных пространствах воркера
    main_module = sys.modules.get("__main__")
    if main_module and hasattr(main_module, "worker_model_holder"):
        model = main_module.worker_model_holder.get("mini_lm")

    if not model:
        worker_module = sys.modules.get("parse_and_create_events_worker")
        if worker_module and hasattr(worker_module, "worker_model_holder"):
            model = worker_module.worker_model_holder.get("mini_lm")

    if not model:
        try:
            from Event_Pulse_app.main import model_holder
            model = model_holder.get("mini_lm")
        except (ImportError, ModuleNotFoundError):
            pass

    if not model:
        return None

    return model.encode(text, convert_to_tensor=True)


# =====================================================================
# УРОВЕНЬ 2: КЭШ ПОЛНЫХ ПАР СРАВНЕНИЯ
# =====================================================================
@lru_cache(maxsize=4096)
def _core_vector_match(query_text: str, event_text: str, threshold: float) -> bool:
    """Проверяет кэш пар. Если пары нет — берет векторы и считает Cos-Sim."""
    query_embedding = get_cached_embedding(query_text)
    event_embedding = get_cached_embedding(event_text)

    if query_embedding is None or event_embedding is None:
        return False

    similarity = util.cos_sim(query_embedding, event_embedding).item()
    matched = similarity >= threshold

    # Лог пишется синхронно в файл вместо print — быстрая и дешёвая операция,
    # не блокирует event loop надолго (запись в ОС-буфер, не на диск напрямую)
    # with open("logs/similarity_log.txt", "a", encoding="utf-8") as f:
    #     f.write(f"{similarity:.4f}\t{matched}\t'{query_text}' <-> '{event_text}'\n")

    return matched


# =====================================================================
# УРОВЕНЬ 3: ПУБЛИЧНЫЙ ИНТЕРФЕЙС
# =====================================================================
def fuzzy_match(query: EventQuery, raw_event: dict, threshold: float = 0.7) -> bool:
    """Точка входа: нормализует строки и отправляет в кэш пар."""
    threshold = float(os.getenv("FUZZY_THRESHOLD", threshold))
    
    query_text = query.query_text.strip().lower()
    event_text = raw_event.get("title", "").strip().lower()

    if not query_text or not event_text:
        return False

    return _core_vector_match(query_text, event_text, threshold)


# =====================================================================
# УТИЛИТА ДЛЯ МОНИТОРИНГА (ОПЦИОНАЛЬНО)
# =====================================================================
# def print_cache_diagnostics():
#     """Выводит общую статистику кэша. Можно вызывать раз в цикл в parser_loop."""
#     emb_info = get_cached_embedding.cache_info()
#     match_info = _core_vector_match.cache_info()
#     print(f"📊 [КЭШ ВЕКТОРОВ] Попаданий: {emb_info.hits}, Промахов: {emb_info.misses}")
#     print(f"📊 [КЭШ ПАР МЭТЧИНГА] Попаданий: {match_info.hits}, Промахов: {match_info.misses}")