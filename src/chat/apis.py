import asyncio
import json
from fastapi import WebSocket, APIRouter
from database import get_collection, get_db_session
from src.chat.controllers import (
    get_chat_history,
    get_context,
    get_last_questions,
    preprocess_text,
)
from src.tasks.controllers import TaskController
from src.tasks.serializers import CreateTaskSchema
from src.tasks.task import chat_task_creation
from sqlalchemy.orm import Session
from fastapi import Depends
from pymongo.synchronous.collection import Collection
from src.utils.log import logger_set

router = APIRouter()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db_session),
    collection: Collection = Depends(get_collection),
):
    """
    Args:
        websocket (WebSocket): WebSocket connection object
        session_id (str): Unique identifier for the chat session
        db (Session): Database session dependency
        collection (Collection): MongoDB collection dependency

    This endpoint:
        - Accepts WebSocket connections
        - Manages chat history and context
        - Creates and processes chat tasks
        - Handles response streaming back to client

    Returns:
        None: Maintains WebSocket connection until closed or error occurs

    Raises:
        Exception: Sends error message over WebSocket if any error occurs
    """
    try:
        logger_set.info(f"Session id: {session_id} - websocket connection request")
        await websocket.accept()  # Accept websocket connection
        logger_set.info(f"Session id: {session_id} - websocket connection accepted")

        # Get the session chat if available else create session chat with provided ID
        if not collection.find_one({"_id": session_id}):
            collection.insert_one({"_id": session_id, "chat": []})
        all_chat_history = await get_chat_history(collection, session_id)

        # Sent previous chat history
        await websocket.send_json(
            {
                "message": "Chat history",
                "data": {
                    "chats": json.dumps(
                        [
                            {k: str(v) for k, v in chat.items()}
                            for chat in all_chat_history["chat"]
                        ]
                    ),
                },
                "error_msg": "",
                "error": "",
            }
        )
        while True:
            # Get the data from the websocket
            data = await websocket.receive_json()

            # fetch last 15 (limit=) chats
            chat_history = await get_last_questions(collection, session_id, limit=15)
            logger_set.info(f"Session id: {session_id} - data recieved")

            # preproccess the chats (word tokenization, stop word and stemming)
            logger_set.info(f"Session id: {session_id} - preproccessing stared")
            query_chats = []
            response_chats = []
            query_context = []
            res_context = []
            if chat_history["chat"]:
                for chat in chat_history["chat"]:
                    query_chats.append(await preprocess_text(chat["query"]))
                    response_chats.append(await preprocess_text(chat["response"]))

                query_context = await get_context(query_chats, data["description"])
                res_context = await get_context(response_chats, data["description"])
                if len(response_chats) >= 1 and response_chats[-1] not in res_context:
                    res_context.append(response_chats[-1])
                if len(response_chats) >= 2 and response_chats[-2] not in res_context:
                    res_context.append(response_chats[-2])
            logger_set.info(f"Session id: {session_id} - preproccessing completed")

            # create task and sent acknowledgement - task is processing
            task = CreateTaskSchema(**data)
            logger_set.info(f"Session id: {session_id} - chat task creation")
            new_task = await TaskController.create_tasks_ctrl(db, task)
            logger_set.info(f"Session id: {session_id} - chat task created")

            await websocket.send_json(
                {
                    "message": "Processing task",
                    "data": {
                        "id": new_task.id,
                    },
                    "error_msg": "",
                    "error": "",
                }
            )
            logger_set.info(
                f"Session id: {session_id} - chat task started {new_task.id}"
            )

            # create task using asyncio and sent the response of the task
            asyncio.create_task(
                chat_task_creation(
                    websocket=websocket,
                    db=db,
                    collection=collection,
                    session_id=session_id,
                    agent_id=task.agent_id,
                    task_id=new_task.id,
                    include_previous_output=task.include_previous_output,
                    previous_output=task.previous_output,
                    previous_queries=query_context,
                    previous_responses=res_context,
                )
            )
            logger_set.info(
                f"Session id: {session_id} - chat task completed {new_task.id}"
            )
    except Exception as e:
        logger_set.info(f"Session id: {session_id} - error occured {str(e)}")
        error_message = {
            "message": "An error occurred, please try again.",
            "data": {},
            "error_msg": str(e),
            "error": "websocket_error",
        }
        await websocket.send_json(error_message)
