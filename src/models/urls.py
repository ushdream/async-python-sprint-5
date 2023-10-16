from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from .base import Base


class URLs(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url_original = Column(String(256), unique=True, nullable=False)
    url_short = Column(String(256), unique=True, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    deleted = Column(Boolean, unique=False, nullable=True)




