from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .base import Base


class URLLogger(Base):
    __tablename__ = 'url_logger'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url_short = Column(String(256), unique=False, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    by_user = Column(String(128), unique=False, nullable=True)
