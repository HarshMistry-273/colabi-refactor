from langchain_text_splitters import CharacterTextSplitter
from src.config import Config
from langchain_openai import OpenAIEmbeddings

# Langchain embeddings and splitter that will be use
embeddings = OpenAIEmbeddings(
    api_key=Config.OPENAI_API_KEY, model="text-embedding-3-small"
)

splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
