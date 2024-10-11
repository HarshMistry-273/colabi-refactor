from uuid import uuid4
from datetime import time
from src.preprocessing import embeddings, splitter
from src.celery import celery_app
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents.base import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
)


def get_uuid():
    return str(uuid4())


class PineConeConfig:
    def __init__(
        self,
        api_key: str,
        index_name: str,
        namespace: str = None,
        file_path: str = None,
        file_type: str = None,
    ):
        self.api_key = api_key
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.create_index_if_not_exist()
        self.index = self.pc.Index(index_name)

        self.namespace = namespace
        self.vector_store = None
        if self.namespace:
            self.vector_store = PineconeVectorStore(
                index=self.index, embedding=embeddings, namespace=self.namespace
            )
            
        self.docs = None
        if file_path:
            self.docs = self.load_and_split_document(file_path, file_type)
            self.add_documents()

    def create_index_if_not_exist(self) -> None:
        existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]

        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        while not self.pc.describe_index(self.index_name).status["ready"]:
            time.sleep(1)

    def add_documents(self) -> None:
        self.vector_store.add_documents(documents=self.docs, ids=self.index_name)

    def load_and_split_document(
        self, url: str, file_type: str, splitter=splitter
    ) -> list[Document]:
        if file_type.lower() == "csv":
            docs = CSVLoader(url).load_and_split(splitter)
            return docs
        elif file_type.lower() == "pdf":
            docs = PyPDFLoader(url).load_and_split(splitter)
            return docs
        elif file_type.lower() == "txt":
            docs = TextLoader(url).load_and_split(splitter)
            return docs
        else:
            raise Exception("Provided file type is not supported")
