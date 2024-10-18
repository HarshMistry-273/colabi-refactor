from sqlalchemy import String, DateTime, Column, Text, JSON, Boolean
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
    focus_group_title = Column(String(255), nullable=True)
    focus_group_description = Column(Text, nullable=True)
    focus_group_objective = Column(Text, nullable=True)
    discussion_topic = Column(Text, nullable=True)
    top_ideas = Column(JSON, nullable=True)
    validation_survey_title = Column(String(255), nullable=True)
    questions = Column(JSON, nullable=True)
    file_upload = Column(Boolean, nullable=True)
    context = Column(String(255), nullable=True)
    file_url = Column(String(255), nullable=True)
    is_custom_agent = Column(Boolean, default=False, nullable=False)
    vector_id = Column(String(36), nullable=True)
    is_chatbot = Column(Boolean, default=False)

    task = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
