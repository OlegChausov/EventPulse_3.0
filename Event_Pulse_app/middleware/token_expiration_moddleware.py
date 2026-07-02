from datetime import datetime, timedelta, timezone
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError
from starlette.responses import RedirectResponse
from Event_Pulse_app.config import SEMI_PUBLIC_PATHS, PUBLIC_PATHS
from Event_Pulse_app.utils.auth_jwt import decode_access_token, create_access_token
from dotenv import load_dotenv
import os


load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SLIDING_THRESHOLD_MINUTES = int(os.getenv("SLIDING_THRESHOLD_MINUTES"))  # если осталось меньше — продлеваем

class SlidingExpirationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in SEMI_PUBLIC_PATHS):
            return await call_next(request)

        try:
            token = request.cookies["access_token"]
            payload = decode_access_token(token)

            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            now = datetime.now(timezone.utc)

            if exp < now:
                return RedirectResponse(url="/login")

            if (exp - now) < timedelta(minutes=SLIDING_THRESHOLD_MINUTES):
                new_token = create_access_token({"sub": payload["sub"]})
                response = await call_next(request)
                response.set_cookie(
                    key="access_token",
                    value=new_token,
                    httponly=True,
                    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    samesite="lax",
                    secure=True
                )
                return response


        except (JWTError, KeyError, ValueError):
            # токен битый — не продлеваем, просто пропускаем
            return await call_next(request)

        return await call_next(request)

