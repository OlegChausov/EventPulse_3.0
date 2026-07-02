from Event_Pulse_app.utils.set_translation_to_request_state import set_translation_to_request_state
from fastapi.responses import Response
from fastapi import APIRouter, Request, Form, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import RedirectResponse
from Event_Pulse_app.database import get_db
from Event_Pulse_app.models import User, EventQuery

from sqlalchemy.future import select
from sqlalchemy import delete

from Event_Pulse_app.utils.template_functions import templates
from Event_Pulse_app.utils.QueryNormalizer import QueryNormalizer
from typing import List, Optional



router = APIRouter()
router1 = APIRouter()
router2 = APIRouter()
router3 = APIRouter()
router4 = APIRouter()


@router.get("/profile/query/list")
async def query_list(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id

    if user_id is None:
        return templates.TemplateResponse("partials/quaries_error.html", {"request": request, "message": "Пользователь не найден"} )

    result = await db.execute(select(EventQuery).where(EventQuery.user_id == user_id))
    queries = result.scalars().all()

    result_user = await db.execute(select(User).where(User.id == user_id))
    user = result_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    set_translation_to_request_state(user, request)

    return templates.TemplateResponse("partials/query_list.html", {"request": request, "queries": queries, "success" : True})


@router1.get("/profile/query/form")
async def query_form(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    result_user = await db.execute(select(User).where(User.id == user_id))
    user = result_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    set_translation_to_request_state(user, request)
    return templates.TemplateResponse("partials/query_form.html", {"request": request})

@router2.post("/profile/query/add")
async def add_query(
    request: Request,
    db: AsyncSession = Depends(get_db),
    query_text: str = Form(...),
    query_type: str = Form(...)
):
    user_id = request.state.user_id

    await db.execute(
        delete(EventQuery).where(
            EventQuery.user_id == user_id,
            EventQuery.query_text == query_text
        )
    )

    query = EventQuery(
        user_id=user_id,
        query_text=query_text,
        preprocessed_name=QueryNormalizer.preprocess(query_text, query_type),
        query_type=query_type,
        is_active=True
    )
    db.add(query)
    await db.commit()

    result_user = await db.execute(select(User).where(User.id == user_id))
    user = result_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    set_translation_to_request_state(user, request)

    result = await db.execute(select(EventQuery).where(EventQuery.user_id == user_id))
    queries = result.scalars().all()
    return templates.TemplateResponse("partials/query_list.html", {"request": request, "queries": queries})

@router3.post("/profile/query/deactivate/{query_id}")
async def deactivate_query(query_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EventQuery).where(EventQuery.id == query_id))
    query = result.scalar_one_or_none()
    if query:
        query.is_active = False
        await db.commit()

    user_id = request.state.user_id
    result = await db.execute(select(EventQuery).where(EventQuery.user_id == user_id))
    queries = result.scalars().all()
    return templates.TemplateResponse("partials/query_list.html", {"request": request, "queries": queries})


@router.post("/profile/query/query_bulk")
async def query_bulk(
    selected_queries: Optional[List[int]] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    success_count = 0
    fail_count = 0

    if not selected_queries:
        # ничего не делаем, просто возвращаем пустой ответ
        return Response(status_code=204)

    for query_id in selected_queries:
        obj = await db.get(EventQuery, query_id)
        if not obj:
            print(f"запрос с id {query_id} не найдено для действия deactivate_query")
            fail_count += 1
            continue
        try:
            obj.is_active = False
            success_count += 1
            db.add(obj)

        except Exception as e:
            print(f"Ошибка при деактивации EventQuery: {obj.id} {e}")

    await db.commit()

    return RedirectResponse(url="/profile", status_code=303)
