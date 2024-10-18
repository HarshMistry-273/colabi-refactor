import asyncio
import json
from fastapi import WebSocket, APIRouter
from database import get_collection, get_db_session
from src.chat.controllers import get_context, get_last_questions, preprocess_text
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
    try:
        logger_set.info(f"Session id: {session_id} - websocket connection request")
        await websocket.accept()
        logger_set.info(f"Session id: {session_id} - websocket connection accepted")

        if not collection.find_one({"_id": session_id}):
            collection.insert_one({"_id": session_id, "chat": []})
        chat_history = await get_last_questions(collection, session_id, limit=10)

        await websocket.send_json(
            {
                "message": "Chat history",
                "data": {
                    "chats": json.dumps(
                        [
                            {k: str(v) for k, v in chat.items()}
                            for chat in chat_history["chat"]
                        ]
                    ),
                },
                "error_msg": "",
                "error": "",
            }
        )
        while True:
            chat_history = await get_last_questions(collection, session_id, limit=15)
            data = await websocket.receive_json()
            logger_set.info(f"Session id: {session_id} - data recieved")

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
