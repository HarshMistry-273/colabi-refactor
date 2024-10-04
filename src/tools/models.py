from sqlalchemy import String, DateTime, Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, UTC
from src.agents.models import Agent
from src.utils.utils import get_uuid


class Tool(Base):
    __tablename__ = "tools"

    id = Column(
        String(36), primary_key=True, index=True, nullable=False, default=get_uuid
    )
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.now(tz=UTC))

    agent = relationship("Agent", back_populates="tool")
