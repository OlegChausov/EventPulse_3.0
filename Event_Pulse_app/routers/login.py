import os

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from Event_Pulse_app.database import get_db
from Event_Pulse_app.models import User
from Event_Pulse_app.utils.password import verify_password
from sqlalchemy.future import select
from Event_Pulse_app.utils.auth_jwt import create_access_token
from dotenv import load_dotenv
from Event_Pulse_app.utils.template_functions import templates

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


router = APIRouter()


@router.get("/login")
async def login_page(request: Request):
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return RedirectResponse(url=f"/profile")
    return templates.TemplateResponse("login.html", {"request": request})


# Обработка логина
@router.post("/login")
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    name_or_email = form.get("name_or_email")
    password = form.get("password")

    if not name_or_email or not password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Введите имя пользователя/email и пароль", "success": False}
        )

    result = await db.execute(
        select(User).where(
            (User.name == name_or_email) | (User.email == name_or_email)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Неверное имя пользователя или Email", "success": False}
        )

    if not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Неверный пароль", "success": False}
        )

    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=True
    )
    return response