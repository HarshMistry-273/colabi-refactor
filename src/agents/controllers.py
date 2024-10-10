from datetime import time
import os
import shutil
from src.agents.models import Agent
from fastapi import HTTPException, UploadFile
from src.agents.serializers import get_agent_serializer, UpdateCustomAgent
from sqlalchemy.orm import Session
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
)
from src.agents.task import embedded_docs
from src.config import Config
from langchain_core.documents.base import Document
from src.preprocessing import splitter, embeddings
from src.utils.utils import get_uuid
from langchain_pinecone import PineconeVectorStore


# def load_and_split_document(url: str, file_type: str, splitter) -> list[Document]:
#     if file_type.lower() == "csv":
#         docs = CSVLoader(url).load_and_split(splitter)
#         return docs
#     elif file_type.lower() == "pdf":
#         docs = PyPDFLoader(url).load_and_split(splitter)
#         return docs
#     elif file_type.lower() == "txt":
#         docs = TextLoader(url).load_and_split(splitter)
#         return docs
#     else:
#         raise Exception("Provided file type is not supported")


# class PineConeConfig:
#     def __init__(
#         self,
#         api_key: str,
#         index_name: str,
#         namespace: str,
#         file_path: str,
#         file_type: str,
#     ):
#         self.api_key = api_key
#         self.pc = Pinecone(api_key=api_key)
#         self.index_name = index_name
#         self.create_index_if_not_exist()
#         self.index = self.pc.Index(index_name)
#         self.namespace = namespace
#         self.vector_store = PineconeVectorStore(
#             index=self.index, embedding=embeddings, namespace=self.namespace
#         )
#         self.docs = load_and_split_document(file_path, file_type)
#         self.add_documents()

#     def create_index_if_not_exist(self) -> None:
#         existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]

#         if self.index_name not in existing_indexes:
#             self.pc.create_index(
#                 name=self.index_name,
#                 dimension=1536,
#                 metric="cosine",
#                 spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#             )

#         while not self.pc.describe_index(self.index_name).status["ready"]:
#             time.sleep(1)

#     def add_documents(self) -> None:
#         self.vector_store.add_documents(documents=self.docs, ids=self.index_name)

#     def load_and_split_document(
#         self, url: str, file_type: str, splitter=splitter
#     ) -> list[Document]:
#         if file_type.lower() == "csv":
#             docs = CSVLoader(url).load_and_split(splitter)
#             return docs
#         elif file_type.lower() == "pdf":
#             docs = PyPDFLoader(url).load_and_split(splitter)
#             return docs
#         elif file_type.lower() == "txt":
#             docs = TextLoader(url).load_and_split(splitter)
#             return docs
#         else:
#             raise Exception("Provided file type is not supported")


class AgentController:

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def create_custom_agent_ctrl(
        db: Session,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: str,
        payload: dict,
        file: UploadFile,
    ):
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

            custom_agent = Agent(
                name=name,
                role=role,
                goal=goal,
                backstory=backstory,
                tools=tools,
                vector_id=namespace,
                file_url=file_path,
                **dict(payload),
            )
            db.add(custom_agent)
            db.commit()
            db.refresh(custom_agent)

            return get_agent_serializer(custom_agent)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def update_custom_agent_ctrl(db: Session, id, updated_agent: UpdateCustomAgent):
        try:
            if id:
                agent = db.query(Agent).filter(Agent.id == id).first()
            if not agent:
                raise HTTPException(status_code=400, detail="Agent not Found")

            for field, value in updated_agent.model_dump(exclude_unset=True).items():
                setattr(agent, field, value)

            db.commit()
            db.refresh(agent)
            return get_agent_serializer(agent)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
