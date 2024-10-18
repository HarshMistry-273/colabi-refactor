from typing import Any, Dict, List, Optional
from src.agents.models import Agent
from pydantic import BaseModel
from datetime import datetime


class GetAgentSchema(BaseModel):
    id: str
    name: str
    role: str
    goal: str
    backstory: str
    tools: list[str]
    created_at: datetime


class CreateAgentSchema(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: Optional[list[str]]
    is_chatbot: Optional[bool] = False


class UpdateCustomAgent(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    tools: Optional[list[str]] = None
    focus_group_title: Optional[str] = None
    focus_group_description: Optional[str] = None
    focus_group_objective: Optional[str] = None
    discussion_topic: Optional[str] = None
    top_ideas: Optional[list[str]] = None
    validation_survey_title: Optional[str] = None
    questions: Optional[list[dict]] = None
    file_upload: Optional[bool] = None
    file_url: Optional[str] = None
    context: Optional[str] = None
    file_type: Optional[str] = None
    upload_url: Optional[str] = None
    is_chatbot: Optional[bool] = None


def get_agent_serializer(agents: list[Agent]) -> list[dict]:
    agents_list = []

    if not isinstance(agents, list):
        agents = [agents]

    for agent in agents:
        if agent.is_custom_agent:
            agents_list.append(
                {
                    "id": agent.id,
                    "name": agent.name,
                    "goal": agent.goal,
                    "backstory": agent.backstory,
                    "tools": agent.tools,
                    "role": agent.role,
                    "focus_group_title": agent.focus_group_description,
                    "focus_group_description": agent.focus_group_description,
                    "focus_group_objective": agent.focus_group_objective,
                    "discussion_topic": agent.discussion_topic,
                    "top_ideas": agent.top_ideas,
                    "validation_survey_title": agent.validation_survey_title,
                    "questions": agent.questions,
                    "file_upload": agent.file_upload,
                    "file_url": agent.file_url,
                    "context": agent.context,
                    "is_custom_agent": agent.is_custom_agent,
                    "vector_id": agent.vector_id,
                    "is_chatbot": agent.is_chatbot,
                }
            )
        else:
            agents_list.append(
                {
                    "id": agent.id,
                    "name": agent.name,
                    "goal": agent.goal,
                    "backstory": agent.backstory,
                    "tools": agent.tools,
                    "role": agent.role,
                    "is_chatbot": agent.is_chatbot,
                    "is_custom_agent": agent.is_custom_agent,
                }
            )

    return agents_list
