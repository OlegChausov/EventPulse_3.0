from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from jose import JWTError
from Event_Pulse_app.utils.auth_jwt import decode_access_token
from Event_Pulse_app.config import SEMI_PUBLIC_PATHS, PUBLIC_PATHS


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        path = request.url.path
        # если путь публичный — пропускаем без проверки
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        token = request.cookies.get("access_token")
        # если нет токена
        if not token:
            # если маршрут полупубличный
            if any(path.startswith(p) for p in SEMI_PUBLIC_PATHS):
                # нет токена, но маршрут разрешён → просто идём дальше
                return await call_next(request)
            else:
                # защищённый маршрут → редирект
                return RedirectResponse(url="/login")

        # Пробуем декодировать токен
        try:
            payload = decode_access_token(token)
            request.state.user_id = int(payload["sub"])
        except (JWTError, KeyError, TypeError, ValueError) as e:
            if any(path.startswith(p) for p in SEMI_PUBLIC_PATHS):
                return await call_next(request)
            return RedirectResponse(url="/login")

        # передаём управление дальше (роутеру или следующему middleware)
        return await call_next(request)
