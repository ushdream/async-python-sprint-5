from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from .base import Base


class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_uuid = Column(String(96))
    file_path = Column(String(256))
    file_name = Column(String(256), nullable=False)
    size = Column(Integer, nullable=False)
    is_downloadable = Column(Boolean, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
