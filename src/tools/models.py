from sqlalchemy import String, DateTime, Column, Text
from database import Base
from datetime import datetime, UTC
from src.utils.utils import get_uuid


class Tool(Base):
    __tablename__ = "tools"

    id = Column(
        String(36), primary_key=True, index=True, nullable=False, default=get_uuid
    )
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(tz=UTC))
