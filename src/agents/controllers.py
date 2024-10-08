from src.agents.models import Agent
from fastapi import HTTPException
from src.agents.serializers import get_agent_serializer
from sqlalchemy.orm import Session


def get_agents_ctrl(db: Session, id) -> list[dict]:
    try:
        if id:
            agents = db.query(Agent).filter(Agent.id == id).all()
        else:
            agents = db.query(Agent).all()
        agents = get_agent_serializer(agents)
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_agent_ctrl(db: Session, agent: Agent):
    try:
        new_agent = Agent(
            name=agent.name,
            role=agent.role,
            goal=agent.goal,
            backstory=agent.backstory,
            tools=agent.tools,
        )
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)

        return get_agent_serializer(new_agent)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
