from sqlalchemy import String, DateTime, Column, Text, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, UTC
from src.utils.utils import get_uuid


class Agent(Base):
    __tablename__ = "agents"

    id = Column(
        String(36), primary_key=True, index=True, nullable=False, default=get_uuid
    )
    name = Column(String(255), nullable=False)
    role = Column(Text, nullable=False)
    goal = Column(Text, nullable=False)
    backstory = Column(Text, nullable=False)
    tools = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(tz=UTC))

    task = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
