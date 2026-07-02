import asyncio
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from Event_Pulse_app.config import PARSER_REFRESH_INTERVAL_SECONDS, CACHE_TTL_HOURS
from Event_Pulse_app.models import User, Event, EventQuery
from Event_Pulse_app.database import AsyncSessionLocal
from Event_Pulse_app.utils.parse_all import run_all_parsers
from Event_Pulse_app.utils.fuzzy_match import fuzzy_match
from Event_Pulse_app.utils.QueryNormalizer import QueryNormalizer
from Event_Pulse_app.utils.send_an_email import send_email


async def process_user_events(user: User, parsed_events: dict[str, list[dict]], db: AsyncSession):
    """
    Сопоставляет поисковые запросы конкретного пользователя с распарсенными событиями
    и отправляет email-уведомление при обнаружении совпадений.
    """
    # 1. Загружаем поисковые запросы пользователя
    stmt = await db.execute(select(EventQuery).where(EventQuery.user_id == user.id))
    user_event_queries = stmt.scalars().all()

    raw_films = parsed_events.get("films", [])
    raw_concerts = parsed_events.get("concerts", [])

    # Если новых событий вообще нет — тихо выходим без исключений
    if not raw_films and not raw_concerts:
        return

    # Загружаем URL уже существующих событий пользователя, чтобы избежать дубликатов
    event_stmt = await db.execute(select(Event.url).where(Event.user_id == user.id))
    old_user_events_urls = set(event_stmt.scalars().all())

    list_of_new_events = []
    processed_urls = set()

    # 2. Мэтчинг запросов с событиями
    for user_query in user_event_queries:
        # Определяем нужный пул событий в зависимости от типа запроса
        target_events = raw_films if user_query.query_type == "film" else raw_concerts

        for raw_event in target_events:
            event_url = raw_event.get("url")
            if not event_url:
                continue

            # Исключаем дубликаты
            if event_url in old_user_events_urls or event_url in processed_urls:
                continue

            # Векторный ИИ-мэтч
            if fuzzy_match(user_query, raw_event):
                new_event = Event(
                    user_id=user.id,
                    event_query_id=user_query.id,
                    title=raw_event.get("title"),
                    preprocessed_title=QueryNormalizer.preprocess(raw_event["title"], user_query.query_type),
                    url=event_url,
                    location=raw_event.get("location"),
                )
                try:
                    db.add(new_event)
                    list_of_new_events.append(new_event)
                    processed_urls.add(event_url)
                except Exception as e:
                    print(f"❌ {raw_event.get('title')} не обработалось: {e}")

    # 3. Отправка уведомлений и сохранение
    if list_of_new_events:
        # Сначала фиксируем изменения в базе данных
        await db.commit()
        print(f"🔥 Найдено новых событий для пользователя {user.id}: {len(list_of_new_events)}")

        # Формируем тело письма
        mail_lines = []
        for event in list_of_new_events:
            line_parts = [event.title, event.location, event.url]
            mail_lines.append(" | ".join(filter(None, line_parts)))
        
        mail_body = "\n".join(mail_lines)
        recipient = user.second_email if user.second_email else user.email

        # Отправляем уведомление
        try:
            await send_email(recipient, "Event_Pulse нашел новые события для вас!", mail_body)
            print(f"📧 Письмо успешно отправлено на {recipient}")
        except Exception as email_err:
            print(f"❌ Ошибка отправки письма для {recipient}: {email_err}")


async def parser_loop():
    print("⏳ [PARSER LOOP] Фоновый диспетчер запущен...")
    
    last_cache_clear_time = datetime.now()
    cache_ttl = timedelta(hours=CACHE_TTL_HOURS)
    
    while True:
        async with AsyncSessionLocal() as db:
            try:
                # 1. Сбор данных
                print("🌐 [PARSER LOOP] Начинаем сбор данных с сайтов-афиш...")
                parsed_events = await run_all_parsers()
                print("✅ [PARSER LOOP] Парсинг завершен успешно.")
                
                await asyncio.sleep(2)

                # 2. Получение пользователей
                result = await db.execute(select(User))
                users = result.scalars().all()

                # 3. ИИ-мэтчинг (исправленный одиночный цикл)
                print(f"🤖 [PARSER LOOP] Запуск ИИ-мэтчинга для {len(users)} пользователей...")
                for user in users:
                    try:
                        await process_user_events(user, parsed_events, db)
                    except Exception as e:
                        await db.rollback()
                        print(f"❌ Ошибка обработки пользователя {user.id}: {type(e).__name__}: {e}")

                # 4. Управление кэшем эмбеддингов
                current_time = datetime.now()
                if current_time - last_cache_clear_time >= cache_ttl:
                    try:
                        from Event_Pulse_app.utils.fuzzy_match import get_cached_embedding, _core_vector_match
                        get_cached_embedding.cache_clear()
                        _core_vector_match.cache_clear()
                        
                        last_cache_clear_time = current_time
                        print(f"🧹 [💥 ПЛАНОВАЯ ОЧИСТКА] Кэш эмбеддингов успешно сброшен по истечении {CACHE_TTL_HOURS} ч.")
                    except Exception as cache_err:
                        print(f"⚠️ Не удалось очистить кэш: {cache_err}")
                else:
                    time_left = cache_ttl - (current_time - last_cache_clear_time)
                    hours_left = int(time_left.total_seconds() // 3600)
                    minutes_left = int((time_left.total_seconds() % 3600) // 60)
                    print(f"🧠 [PARSER LOOP] Кэш сохранен. До планового сброса осталось: {hours_left}ч {minutes_left}м.")

                print(f"💤 [PARSER LOOP] Засыпаем на {PARSER_REFRESH_INTERVAL_SECONDS} секунд...")
                await asyncio.sleep(PARSER_REFRESH_INTERVAL_SECONDS)

            except Exception as loop_err:
                print(f"💥 [PARSER LOOP] Критическая ошибка в цикле: {loop_err}")
                await asyncio.sleep(10)