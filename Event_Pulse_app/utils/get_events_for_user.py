# # get_events_for_users.py
# from fastapi import APIRouter, Request, Form, Depends, HTTPException
# from fastapi.responses import RedirectResponse
# from fastapi.templating import Jinja2Templates
# from sqlalchemy.ext.asyncio import AsyncSession
# from Event_Pulse_app.database import get_db
# from Event_Pulse_app.models import User, Event, EventQuery
# from Event_Pulse_app.utils.fuzzy_match import fuzzy_match
# from Event_Pulse_app.utils.password import hash_password
# from sqlalchemy.future import select
# from Event_Pulse_app.utils.QueryNormalizer import QueryNormalizer

# from Event_Pulse_app.utils.send_an_email import send_email



# async def create_events(user: User, parsed_events: dict[str, list[dict]], db: AsyncSession):

#     list_of_new_events = []

#     # 1. Загружаем поисковые запросы пользователя
#     stmt = await db.execute(select(EventQuery).where(EventQuery.user_id == user.id))
#     user_event_queries = stmt.scalars().all()

#     # Извлекаем списки из нашего нового структурированного словаря
#     raw_films = parsed_events.get("films", [])
#     raw_concerts = parsed_events.get("concerts", [])

#     if not raw_films and not raw_concerts:
#         raise HTTPException(status_code=400, detail="Нет распарсенных событий")

#     # 2. Загружаем уже существующие URL, чтобы не дублировать
#     stmt1 = await db.execute(select(Event.url).where(Event.user_id == user.id))
#     old_user_events_urls = set(stmt1.scalars().all()) # set() для моментального поиска за O(1)

#     # Список для событий, которые мы уже обработали в этом запуске (вместо .remove)
#     processed_urls = set()

#     for user_query in user_event_queries:
#         # ОПРЕДЕЛЯЕМ ПОТОК ДАННЫХ:
#         # Если у юзера запрос на фильм — берем только фильмы. Если на концерт — только концерты.
#         if user_query.query_type == "film":
#             current_raw_events = raw_films
#         elif user_query.query_type == "concert":
#             current_raw_events = raw_concerts
#         else:
#             current_raw_events = raw_films + raw_concerts  # На случай, если тип не указан

#         for raw_event in current_raw_events:
#             event_url = raw_event['url']

#             # Быстрые проверки без участия ИИ (экономим кучу ресурсов)
#             if event_url in old_user_events_urls or event_url in processed_urls:
#                 continue

#             # И только теперь запускаем векторный ИИ-мэтч
#             if fuzzy_match(user_query, raw_event):
#                 new_event = Event(
#                     user_id = user.id,
#                     event_query_id = user_query.id,
#                     title = raw_event.get('title'),
#                     preprocessed_title = QueryNormalizer.preprocess(raw_event['title'], user_query.query_type),
#                     url = event_url,
#                     location = raw_event.get('location'),
#                 )
#                 try:
#                     db.add(new_event)
#                     list_of_new_events.append(new_event)
#                     # Вместо удаления из списка, просто помечаем URL как обработанный
#                     processed_urls.add(event_url) 
#                 except Exception as e:
#                     print(f"❌ {raw_event['title']} не обработалось: {e}")

#     # 3. Сохраняем в базу и отправляем email
#     await db.commit()
    
#     print(f"🔥 Найдено новых событий для пользователя: {len(list_of_new_events)}")
    
#     if list_of_new_events:
#         mail_body = "\n".join(
#             " | ".join(filter(None, [event.title, event.location, event.url]))
#             for event in list_of_new_events
#         )
#         recipient = user.second_email if user.second_email else user.email
#         await send_email(recipient, "Event_Pulse нашел новые события для вас!", mail_body)
        
#     return list_of_new_events


