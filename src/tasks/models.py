from sqlalchemy import String, Integer, DateTime, Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, UTC
from src.agents.models import Agent
from src.utils.utils import get_uuid


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        String(36), primary_key=True, index=True, nullable=False, default=get_uuid
    )
    # topic = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    status = Column(String(10), default="processing")
    completed_at = Column(DateTime, nullable=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.now(tz=UTC))
    agent = relationship("Agent", back_populates="task")
