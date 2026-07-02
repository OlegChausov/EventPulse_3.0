from fastapi import APIRouter, Request, Depends, HTTPException
from Event_Pulse_app.utils.set_translation_to_request_state import set_translation_to_request_state
from sqlalchemy.ext.asyncio import AsyncSession
from Event_Pulse_app.database import get_db
from Event_Pulse_app.models import User

from sqlalchemy.future import select

from Event_Pulse_app.utils.template_functions import templates



router = APIRouter()


# @router.get("/profile")
# async def profile(request: Request, db: AsyncSession = Depends(get_db)):
#     user_id = request.state.user_id
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     print(f'в роктере профиль такой реквест стейт: {request.state.__dict__}')
#     return templates.TemplateResponse("profile.html", {
#         "request": request,
#         "user": user,
#     })


@router.get("/profile")
async def profile(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.state.user_id
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    set_translation_to_request_state(user, request)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
    })