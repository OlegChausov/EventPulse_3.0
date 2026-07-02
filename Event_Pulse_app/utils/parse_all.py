# parse_all.py
import asyncio
from datetime import date
from concurrent.futures import ProcessPoolExecutor

from Event_Pulse_app.parsers.afisha_me import get_afisha_me_films
from Event_Pulse_app.parsers.biletai_lt import get_biletai_lt_concerts
from Event_Pulse_app.parsers.concertful import get_concertful_pl
from Event_Pulse_app.parsers.relax_by import get_relax_by_films
from Event_Pulse_app.utils.time_functions import default_start_date, default_end_date


# -----------------------------
# ГЛОБАЛЬНЫЕ ОБЁРТКИ ДЛЯ ПРОЦЕССОВ
# -----------------------------

def run_afisha_me(start_date, end_date):
    return asyncio.run(get_afisha_me_films(start_date, end_date))

def run_biletai_lt(start_date, end_date):
    return asyncio.run(get_biletai_lt_concerts(start_date, end_date))

def run_concertful(start_date):
    return asyncio.run(get_concertful_pl(start_date))

def run_relax_by():
    return asyncio.run(get_relax_by_films())






# -----------------------------
# ОСНОВНАЯ КОРУТИНА (РАЗДЕЛЯЕТ ПОТОКИ ДАННЫХ) # создаём пул процессов (4 воркера)
# -----------------------------
async def run_all_parsers() -> dict[str, list[dict]]:
    start_date = default_start_date()
    end_date = default_end_date(start_date)
    loop = asyncio.get_running_loop()

    names = [
        "afisha.me",
        "biletai.lt",
        "concertful.pl",
        "relax.by"
    ]

    with ProcessPoolExecutor(max_workers=4) as executor:
        tasks = [
            loop.run_in_executor(executor, run_afisha_me, start_date, end_date),
            loop.run_in_executor(executor, run_biletai_lt, start_date, end_date),
            loop.run_in_executor(executor, run_concertful, start_date),
            loop.run_in_executor(executor, run_relax_by),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    separated_events = {"films": [], "concerts": []}

    for name, result in zip(names, results):
        if isinstance(result, Exception):
            print(f"❌ Парсер '{name}' упал: {type(result).__name__}: {result}", flush=True)
            continue

        print(f"✅ Парсер '{name}' вернул {len(result)} событий", flush=True)

        if name in ["afisha.me", "relax.by"]:
            for event in result:
                event["event_type"] = "film"
            separated_events["films"].extend(result)

        elif name in ["biletai.lt", "concertful.pl"]:
            for event in result:
                event["event_type"] = "concert"
            separated_events["concerts"].extend(result)

    print(f"📊 Итого: фильмов={len(separated_events['films'])}, концертов={len(separated_events['concerts'])}", flush=True)
    return separated_events
 


        # -----------------------------------------------------------------
    # # ВРЕМЕННЫЙ БЛОК: Сохраняем чистые заголовки для датасета
    # # -----------------------------------------------------------------
    # import json
    # print(f"DEBUG: Всего концертов для сохранения: {len(separated_events['concerts'])}")
    # if separated_events['concerts']:
    #     print(f"DEBUG: Первый элемент: {separated_events['concerts'][0]}")

    # all_titles = {e.get("title").strip() for e in separated_events["films"] + separated_events["concerts"] if e.get("title")}
    # with open("real_titles_base.txt", "w", encoding="utf-8") as f:
    #     json.dump([[t] for t in all_titles], f, ensure_ascii=False, indent=2)

    # -----------------------------------------------------------------    

