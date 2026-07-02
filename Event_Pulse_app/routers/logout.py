from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter()

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response