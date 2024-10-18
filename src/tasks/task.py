from database import get_db_session_celery
from src.agents.controllers import AgentController
from src.config import Config
from src.crew_agents.custom_agents import CustomAgent
from src.crew_agents.prompts import get_chat_bot_prompt, get_desc_prompt
from src.tasks.controllers import TaskController
from src.tasks.models import Task
from src.tools.controllers import ToolController
from src.utils.utils import PineConeConfig, get_uuid
import pandas as pd
from src.crew_agents.custom_tools import mapping
from src.celery import celery_app
from sqlalchemy.orm import Session
from fastapi import WebSocket
from pymongo.synchronous.collection import Collection
from asgiref.sync import async_to_sync


@celery_app.task()
def task_creation_celery(
    agent_id: str,
    task_id: str,
    base_url: str,
    include_previous_output,
    previous_output,
    is_csv,
):
    with get_db_session_celery() as db:
        agent = async_to_sync(AgentController.get_agents_ctrl)(db, agent_id)
        agent = agent[0]
        task: Task = async_to_sync(TaskController.get_tasks_ctrl)(db, task_id)

        relevant_output = []
        if agent["is_custom_agent"]:
            if agent["file_upload"]:
                namespace = agent["vector_id"]
                ps = PineConeConfig(
                    api_key=Config.PINECONE_API_KEY,
                    index_name=Config.PINECONE_INDEX_NAME,
                    namespace=namespace,
                )

                vector_output = ps.vector_store.similarity_search(
                    query=task.description
                )
                relevant_output = [
                    str(vector_output[i].page_content)
                    for i in range(min(len(vector_output), 2))
                ]

        previous_output = []
        if include_previous_output:
            for task_id in previous_output:
                output = async_to_sync(TaskController.get_tasks_ctrl)(db, task_id)
                previous_output.append(
                    {
                        "description": output.description,
                        "expected_output": output.expected_output,
                        "response": output.response,
                    }
                )

        prompt = get_desc_prompt(
            agent, task.description, previous_output, relevant_output
        )

        agent_tools = agent["tools"]

        tools = []
        for tool in agent_tools:
            agent_tool = async_to_sync(ToolController.get_tools_ctrl)(db, tool)
            tools.append(mapping[agent_tool[0]["name"]])

        init_task = CustomAgent(
            role=agent["role"],
            backstory=agent["backstory"],
            goal=agent["goal"],
            tools=tools,
            expected_output=task.expected_output,
            description=prompt,
        )

        custom_task_output, comment_task_output = async_to_sync(init_task.main)()

        max_length = max(len(v) for v in custom_task_output.json_dict.values())

        # Handle the edge cases in which if we do get empty column
        for key in custom_task_output.json_dict.keys():
            custom_task_output.json_dict[key] += [None] * (
                max_length - len(custom_task_output.json_dict[key])
            )

        full_file_url = None
        if is_csv:
            file_name = f"{get_uuid()}.csv"
            pd.DataFrame(custom_task_output.json_dict).to_csv(
                "static/" + file_name, index=False
            )
            full_file_url = f"{base_url}api/v1/tasks/download/{file_name}"

        async_to_sync(TaskController.update_task_ctrl)(
            db, task_id, custom_task_output.raw, comment_task_output.raw, full_file_url
        )

    return f"Task Completed: {task_id}"


async def chat_task_creation(
    websocket: WebSocket,
    db: Session,
    collection: Collection,
    session_id: int,
    agent_id: str,
    task_id: str,
    include_previous_output,
    previous_output,
    previous_queries,
    previous_responses,
):
    agent = await AgentController.get_agents_ctrl(db, agent_id)
    if not agent:
        await websocket.send_json({"error": "Agent not found"})
        return
    agent = agent[0]
    task: Task = await TaskController.get_tasks_ctrl(db, task_id)
    if not task:
        await websocket.send_json({"error": "Task not found"})
        return

    relevant_output = []
    if agent["is_custom_agent"]:
        if agent["file_upload"]:
            namespace = agent["vector_id"]
            ps = PineConeConfig(
                api_key=Config.PINECONE_API_KEY,
                index_name=Config.PINECONE_INDEX_NAME,
                namespace=namespace,
            )

            try:
                vector_output = ps.vector_store.similarity_search(
                    query=task.description, k=3
                )
                relevant_output = [
                    str(vector_output[i].page_content)
                    for i in range(len(vector_output))
                ]
            except Exception as e:
                await websocket.send_json(
                    {"error": "Pinecone search failed", "details": str(e)}
                )
    relevant_output = []

    previous_output = []
    if include_previous_output:
        for task_id in previous_output:
            output = await TaskController.get_tasks_ctrl(db, task_id)
            previous_output.append(
                {
                    "description": output.description,
                    "expected_output": output.expected_output,
                    "response": output.response,
                }
            )
    prompt = await get_chat_bot_prompt(
        task.description,
        previous_queries,
        previous_responses,
        relevant_document=relevant_output,
    )

    agent_tools = agent["tools"]

    tools = []
    for tool in agent_tools:
        agent_tool = await ToolController.get_tools_ctrl(db, tool)
        tools.append(mapping[agent_tool[0]["name"]])

    init_task = CustomAgent(
        role=agent["role"],
        backstory=agent["backstory"],
        goal=agent["goal"],
        tools=tools,
        expected_output=task.expected_output,
        description=prompt,
        is_chatbot=True,
    )

    try:
        custom_task_output = (
            await init_task.main()
        )  # Ensure this is an async operation if needed
    except Exception as e:
        await websocket.send_json({"error": "Agent task failed", "details": str(e)})
        return

    tasks = await TaskController.update_task_ctrl(
        db, task_id, custom_task_output.raw, None, None
    )
    if tasks:
        try:
            collection.update_one(
                {"_id": session_id},
                {
                    "$push": {
                        "chat": {
                            "chat_id": task.id,
                            "query": tasks.description,
                            "response": tasks.response,
                            "created_at": tasks.created_at,
                        }
                    }
                },
            )
        except Exception as e:
            await websocket.send_json(
                {"error": "Failed to update chat history", "details": str(e)}
            )
    if tasks:
        await websocket.send_json(
            {
                "message": "Task completed",
                "data": {
                    "id": tasks.id,
                    "description": tasks.description,
                    "agent_id": tasks.agent_id,
                    "output": tasks.response,
                    "comment": tasks.comment,
                    "attachments": tasks.attachments,
                    "status": tasks.status,
                    "created_at": str(tasks.created_at),
                },
                "error_msg": "",
                "error": "",
            }
        )
    else:
        await websocket.send_json({"error": "Task update failed"})
