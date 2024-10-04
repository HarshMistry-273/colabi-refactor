from models.model import Agent
from pydantic import BaseModel
from datetime import datetime


class GetAgentSchema(BaseModel):
    id: int
    name: str
    role: str
    goal: str
    backstory: str
    created_at: datetime


class CreateAgentSchema(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str


def get_agent_serializer(agents: list[Agent]):
    agents_list = []
    for agent in agents:
        agents_list.append(
            {
                "id": agent.id,
                "name": agent.name,
                "goal": agent.goal,
                "backstory": agent.backstory,
                "role": agent.role,
            }
        )

    return agents_list
