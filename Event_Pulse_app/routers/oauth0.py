
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
import httpx, os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from Event_Pulse_app.database import get_db
from Event_Pulse_app.models import User
from sqlalchemy import select
from Event_Pulse_app.utils.auth_jwt import create_access_token

load_dotenv()

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")) # 60 это если переменная не задана

OAUTH0_DOMAIN = os.getenv("OAUTH0_DOMAIN")
OAUTH0_CLIENT_ID = os.getenv("OAUTH0_CLIENT_ID")
OAUTH0_REDIRECT_URI = os.getenv("OAUTH0_REDIRECT_URI")
OAUTH0_CLIENT_SECRET = os.getenv("OAUTH0_CLIENT_SECRET")

@router.get("/login/social")
async def login_social():
    return RedirectResponse(
        f"https://{OAUTH0_DOMAIN}/authorize?"
        f"response_type=code&"
        f"client_id={OAUTH0_CLIENT_ID}&"
        f"redirect_uri={OAUTH0_REDIRECT_URI}&"
        f"scope=openid profile email"
    )


router1 = APIRouter()

@router1.get("/login/callback")
async def callback(request: Request, db: AsyncSession = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing code"}

    async with httpx.AsyncClient() as client:
        # 1. Обмен кода на токен
        token_resp = await client.post(f"https://{OAUTH0_DOMAIN}/oauth/token", data={
            "grant_type": "authorization_code",
            "client_id": OAUTH0_CLIENT_ID,
            "client_secret": OAUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": OAUTH0_REDIRECT_URI,
        })
        if token_resp.status_code != 200:
            print("Ошибка при обмене кода на токен:", token_resp.text)
            return RedirectResponse(url="/login/social", status_code=302)

        tokens = token_resp.json()

        # 2. Получение профиля пользователя
        userinfo_resp = await client.get(
            f"https://{OAUTH0_DOMAIN}/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        profile = userinfo_resp.json()

    # Пока просто возвращаем профиль для проверки
    # return profile
    #после получения данных с oauth0


    email = profile.get("email")  # вернёт None, если ключа нет
    if not email:
        print("oauth0 не передал имэйл")
        return RedirectResponse(url=f"/register", status_code=302)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        # если по имэйлу нет пользователя - создаем
        name = profile.get("name", email)  # если не вернулось имя, назовем клиента по имэйлу. Имэйл и имя будут совпадать
        user = User(email=email, name=name)
        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
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
        except Exception as e:
            print(f"Ошибка {e}, Регистрация через oauth0 не удалась, отправляем на повторную")
            return RedirectResponse(url="/login/social")

    try:
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

    except Exception as e:
        print(f"Ошибка {e}, логин через oauth0 не удалася, отправляем на повторный")
        return RedirectResponse(url="/login/social")













