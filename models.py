from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserCreate(BaseModel):
    name: str
