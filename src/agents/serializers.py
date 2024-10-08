from typing import Optional
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
    # focus_group_title: str
    # focus_group_description: str
    # focus_group_objective: str
    # disscussion_topic: str
    # top_idea_1: str
    # top_idea_2: str
    # validaion_servey_title: str
    # questions: list[dict]
    # file_uploaded: bool
    # file_name: str
    # context: str
    # file_type: str
    # upload_url: str


def get_agent_serializer(agents: list[Agent]):
    agents_list = []

    if not isinstance(agents, list):
        agents = [agents]

    for agent in agents:
        agents_list.append(
            {
                "id": agent.id,
                "name": agent.name,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "tools": agent.tools,
                "role": agent.role,
            }
        )

    return agents_list
