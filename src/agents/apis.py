from fastapi import APIRouter
from src.agents.serializers import CreateAgentSchema
from src.agents.controllers import create_agent_ctrl, get_agents_ctrl

router = APIRouter()


@router.get("")
def get_agents(id: int = None):
    all_agents = get_agents_ctrl(id)
    return {"message": "Agents fetched", "agents": all_agents}


@router.post("")
def create_agent(agent: CreateAgentSchema):
    new_agent = create_agent_ctrl(agent)
    return {"message": "Agent created", "agent": new_agent}
