from fastapi import APIRouter, Request, Form, Depends, HTTPException
from Event_Pulse_app.utils.set_translation_to_request_state import set_translation_to_request_state

from sqlalchemy.ext.asyncio import AsyncSession
from Event_Pulse_app.database import get_db
from Event_Pulse_app.models import User
from Event_Pulse_app.utils.password import hash_password
from sqlalchemy.future import select

from Event_Pulse_app.utils.template_functions import templates



router = APIRouter()


@router.get("/profile_edit")
async def profile_edit(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    result_user = await db.execute(select(User).where(User.id == user_id))
    user = result_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    set_translation_to_request_state(user, request)


    return templates.TemplateResponse(
        "profile_edit.html",
        {"request": request, "user": user}
    )

@router.post("/profile_edit")
async def profile_edit(
    request: Request,
    db: AsyncSession = Depends(get_db),
    username: str = Form(...),
    email: str = Form(...),
    second_email: str | None = Form(None),
    preffered_lang: str | None = Form(None),
    new_password: str | None = Form(None),
    new_password_confirmed: str | None = Form(None)
):
    def clean(value: str | None) -> str | None:
        return value.strip() if value else None

    username = clean(username)
    email = clean(email)
    second_email = clean(second_email)
    preffered_lang = clean(preffered_lang)
    new_password = clean(new_password)
    new_password_confirmed = clean(new_password_confirmed)



    user_id = request.state.user_id
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    # Проверка уникальности нового username/email
    result = await db.execute(
        select(User).where(
            ((User.name == username) | (User.email == email)) &
            (User.id != user_id)
        )
    )
    if result.scalar_one_or_none():
        return templates.TemplateResponse(
            "profile_edit.html",
            {   "user": user,
                "request": request,
                "message": "Имя или email уже заняты",
                "success": False
            }
        )


    if new_password:
        if new_password != new_password_confirmed:
            return templates.TemplateResponse(
                "profile_edit.html",
                {   "user": user,
                    "request": request,
                    "message": "Пароли не совпадают",
                    "success": False
                }
            )



    # Обновление данных
    user.name = username
    user.email = email
    user.second_email = second_email
    user.preffered_lang = preffered_lang
    if new_password:
        user.password_hash = hash_password(new_password)

    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        return templates.TemplateResponse(
            "profile_edit.html",
            {"user": user, "request": request,
             "message": "Ошибка при сохранении", "success": False}
        )

    return templates.TemplateResponse(
        "profile_edit.html",
        {"user": user, "request": request, "success": True}
    )