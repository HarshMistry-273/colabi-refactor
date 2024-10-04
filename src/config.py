import os
from dotenv import load_dotenv
# loading the env file
load_dotenv() 

class Config:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
    LANGCHAIN_API_KEY=os.getenv('LANGCHAIN_API_KEY')
    LANGCHAIN_TRACING_V2=os.getenv('LANGCHAIN_TRACING_V2') or "true"
    SERPER_API_KEY=os.getenv('SERPER_API_KEY')
    OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
    # HUB_NAME = "hwchase17/structured-chat-agent"
    MODEL_NAME = os.getenv('MODEL_NAME')
    DATABSE_URL = os.getenv('DATABASE_URL')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
