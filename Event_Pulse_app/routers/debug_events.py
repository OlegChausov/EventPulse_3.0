from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Event_Pulse_app.database import get_db
from sqlalchemy.future import select
from dotenv import load_dotenv
from Event_Pulse_app.models import Event

load_dotenv()

router = APIRouter()


@router.get("/debug/events")
async def debug_events(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Event))
    events = stmt.scalars().all()
    return [
        {

            "title": e.title,
            "preprocessed_title": e.preprocessed_title,
            "location": e.location,
            "matched_query_text": e.matched_query.query_text,
            "matched_query_prep_title": e.matched_query.preprocessed_name
  
        }
        for e in events if e.location == "Vilnius"
    ]
