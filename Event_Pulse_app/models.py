import sys

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from Event_Pulse_app import models
from datetime import datetime
from .db_base import Base  # импорт базового класса
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    second_email = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)    # хэш пароля
    preffered_lang = Column(String, nullable=True)



    queries = relationship(
        "EventQuery",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    events = relationship(
        "Event",
        back_populates="user",
        cascade="all, delete-orphan"
    )



class EventQuery(Base):
    __tablename__ = "event_queries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    query_text = Column(String, nullable=False)
    preprocessed_name = Column(String, nullable=False)
    query_type = Column(Enum("concert", "film", name="query_type"), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="queries")
    matched_events = relationship("Event", back_populates="matched_query")



class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_query_id = Column(Integer, ForeignKey("event_queries.id", ondelete="SET NULL"), nullable=True)

    title = Column(String, nullable=False)
    preprocessed_title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    location = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="events")
    matched_query = relationship("EventQuery", back_populates="matched_events")

