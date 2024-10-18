from datetime import datetime
from crewai import Crew, Agent, Task, Process

# from crewai.memory import LongTermMemory, ShortTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.memory.storage.rag_storage import RAGStorage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# from langchain.memory import ChatMessageHistory
import logging
import pymongo
import time

from src.config import Config
from src.utils.utils import get_uuid

load_dotenv()

try:
    # Creating a MongoClient to connect to the local MongoDB server
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Selecting a specific database named 'your_database_name'
    database = client["colabi"]

    print("Connected to MongoDB")

except Exception as e:
    print(f"Error: {e}")


try:
    collection = database["chat_history"]
except Exception as e:
    print(f"Error: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = ChatOpenAI(
    model=Config.MODEL_NAME,
    api_key=Config.OPENAI_API_KEY,
)

chat_agent = Agent(
    role="Friendly Assistive Chatbot",
    llm=model,
    goal="To assist users in answering questions, and providing support in a conversational and friendly manner, making interactions as smooth and enjoyable as possible.",
    backstory="Created to be a helpful assistant for everyday tasks, this chatbot was developed with empathy and practicality in mind. It is designed to help users by answering queries, provide recommendations, and be an engaging conversational partner."
)

task = Task(
    agent=chat_agent,
    description="Assist the user in a friendly and helpful manner with their question: {question}. Use any relevant context from previous interactions if it helps to provide a better response, without explicitly mentioning the previous context unless necessary. I'll also provide you a context of previous messages send by the user, use those messages in order to assist the user more effectively. History will be \n  Questions: {question}\n Answer: {prev_msg}",
    expected_output="A relevant response based on the user's input."
)

my_crew = Crew(
    agents=[chat_agent],
    tasks=[task],
    verbose=False)

def get_last_questions():
    doc = collection.find_one({"_id": 1})
    if doc and doc['chat']:
        return doc['chat']
    return None

def main():
    while True:
        try:
            if not collection.find_one({"_id": 1}):
                collection.insert_one({"_id": 1, "chat": []})
            question = input("Ask Question to the Bot: ")
            prev_msgs = get_last_questions()

            data = {
                "question": question,
                "previous_questions": [question['user_query'] for question in prev_msgs] if prev_msgs else "",
                "previous_reponse": prev_msgs[-1]['response'] if prev_msgs else "",
                    }
            # if prev_msg:
            #     print(f"previous_question: {prev_msg['user_query']} - {prev_msg['response']}")

            res = my_crew.kickoff(data)

            collection.update_one(
                {"_id": 1},
                {
                    "$push": {
                        "chat": {
                            "chat_id": get_uuid(),
                            "user_query": question,
                            "response": res.raw,
                            "created_at": datetime.now(),
                        }
                    }
                },
            )

            print(res.raw)
            logger.info(f"Question: {question}\nAnswer: {res.raw}")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            print("I'm sorry, but I encountered an error. Please try again.")


if __name__ == "__main__":
    main()

# from crewai import Agent, Task, Crew
# from langchain_community.llms import openai
# from langchain.memory import ConversationSummaryMemory
# from langchain_community.chains import ConversationChain
# from langchain.prompts import PromptTemplate

# # Initialize the language model
# llm = openai(temperature=0.7)

# # Initialize the memory with conversation summary
# memory = ConversationSummaryMemory(llm=llm)

# # Create a custom prompt template
# prompt_template = """Human: {input}

# AI: As an AI assistant, I will respond to your input while considering our conversation history:

# {history}

# Based on this context, here's my response:
# """

# prompt = PromptTemplate(
#     input_variables=["history", "input"], 
#     template=prompt_template
# )

# # Create a conversation chain with summary memory
# conversation = ConversationChain(
#     llm=llm,
#     memory=memory,
#     prompt=prompt,
#     verbose=True
# )

# # Create a chatbot agent
# chatbot_agent = Agent(
#     role='Chatbot',
#     goal='Engage in friendly conversation and answer user queries while maintaining context',
#     backstory='You are a helpful and friendly AI assistant designed to chat with users and provide information on various topics. You can remember and summarize previous parts of the conversation.',
#     verbose=True,
#     allow_delegation=False,
#     llm=llm,
#     tools=[conversation]
# )

# # Define the main chat task
# chat_task = Task(
#     description='Engage in a conversation with the user, answering their questions and providing helpful information. Use your summarized memory to maintain context throughout the conversation.',
#     agent=chatbot_agent
# )

# # Create the crew with just the chatbot agent
# crew = Crew(
#     agents=[chatbot_agent],
#     tasks=[chat_task],
#     verbose=2
# )

# # Function to handle user input and get chatbot response
# def chat_with_bot(user_input):
#     response = crew.kickoff(inputs={'user_input': user_input})
#     return response

# # Main loop for the chat interface
# if __name__ == "__main__":
#     print("Chatbot: Hello! How can I assist you today? (Type 'exit' to end the conversation)")
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == 'exit':
#             print("Chatbot: Goodbye! Have a great day!")
#             break
#         response = chat_with_bot(user_input)
#         print(f"Chatbot: {response}")

#     # Print the final conversation summary
#     print("\nFinal Conversation Summary:")
#     print(memory.load_memory_variables({})["history"])