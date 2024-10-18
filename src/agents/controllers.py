import os
import shutil
from src.agents.models import Agent
from fastapi import HTTPException, UploadFile
from src.agents.serializers import get_agent_serializer
from sqlalchemy.orm import Session
from src.agents.task import embedded_docs
from src.config import Config
from src.utils.utils import get_uuid


class AgentController:

    @staticmethod
    async def get_agents_ctrl(db: Session, id) -> list[dict]:
        try:
            if id:
                agents = db.query(Agent).filter(Agent.id == id).all()
            else:
                agents = db.query(Agent).all()
            agents = get_agent_serializer(agents)
            return agents
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def create_agent_ctrl(db: Session, agent: Agent) -> list[dict]:
        try:
            new_agent = Agent(
                name=agent.name,
                role=agent.role,
                goal=agent.goal,
                backstory=agent.backstory,
                tools=agent.tools,
                is_chatbot=agent.is_chatbot,
            )
            db.add(new_agent)
            db.commit()
            db.refresh(new_agent)

            return get_agent_serializer(new_agent)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def create_custom_agent_ctrl(
        db: Session,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: str,
        is_chatbot: bool,
        payload: dict,
        file: UploadFile,
    ) -> list[dict]:
        try:
            file_path = None
            namespace = None
            if payload.get("file_upload", False):
                file_path = os.path.join(
                    os.path.abspath(os.curdir), "static", file.filename
                )

                # Save uploaded file
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                # Pinecone Configs
                namespace = get_uuid()
                embedded_docs.delay(
                    api_key=Config.PINECONE_API_KEY,
                    index_name=Config.PINECONE_INDEX_NAME,
                    namespace=namespace,
                    file_path=file_path,
                    file_type=file.filename.rsplit(".")[-1],
                )
            else:
                del payload["context"]

            custom_agent = Agent(
                name=name,
                role=role,
                goal=goal,
                backstory=backstory,
                tools=tools,
                vector_id=namespace,
                file_url=file_path,
                is_chatbot=is_chatbot,
                ** dict(payload),
            )
            db.add(custom_agent)
            db.commit()
            db.refresh(custom_agent)

            return get_agent_serializer(custom_agent)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_custom_agent_ctrl(
        db: Session,
        id: str,
        name: str = None,
        role: str = None,
        goal: str = None,
        backstory: str = None,
        tools: str = None,
        payload: dict = None,
        file: UploadFile = None,
    ) -> list[dict]:
        try:
            agent = db.query(Agent).filter(Agent.id == id).first()

            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")

            if name:
                payload.update({"name": name})
            if role:
                payload.update({"role": role})
            if goal:
                payload.update({"goal": goal})
            if backstory:
                payload.update({"backstory": backstory})
            if tools:
                payload.update({"tools": tools})

            file_path = None

            if payload.get("file_upload", False):
                file_path = os.path.join(
                    os.path.abspath(os.curdir), "static", file.filename
                )
                payload["file_url"] = file_path

                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                namespace = get_uuid()
                payload["vector_id"] = namespace
                embedded_docs.delay(
                    api_key=Config.PINECONE_API_KEY,
                    index_name=Config.PINECONE_INDEX_NAME,
                    namespace=namespace,
                    file_path=file_path,
                    file_type=file.filename.rsplit(".")[-1],
                )
            for field, value in payload.items():
                setattr(agent, field, value)

            db.commit()
            db.refresh(agent)
            return get_agent_serializer(agent)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
