from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from .base import Base


class USERs(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(256), unique=True, nullable=False)
    secret_hashed = Column(String(128))
    disabled = Column(bool)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
