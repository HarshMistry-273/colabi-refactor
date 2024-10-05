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
