from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class Info(Base):
    __tablename__ = "infos"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
