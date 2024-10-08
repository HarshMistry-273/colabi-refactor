import os
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, JSONResponse
from database import get_db_session
from src.agents.controllers import get_agents_ctrl
from src.tasks.task import start_agent
from src.crew_agents.custom_agents import CustomAgent
from src.crew_agents.prompts import get_desc_prompt
from src.tasks.serializers import CreateTaskSchema
from src.tasks.controllers import get_tasks_ctrl, create_tasks_ctrl, update_task_ctrl
from src.crew_agents.custom_tools import mapping
import pandas as pd
from src.tools.controllers import get_tools_ctrl
from src.utils.utils import get_uuid

router = APIRouter()


@router.get("")
def get_task(id: str, db: Session = Depends(get_db_session)):
    """
    Retrieve a task by its ID and return its details as a JSON response.

    This function performs the following steps:
    1. Calls the get_tasks_ctrl function with the provided ID to retrieve the task.
    2. Constructs a JSON response containing the task's details.

    Args:
        id (str): The unique identifier of the task to retrieve.

    Returns:
        JSONResponse: A response containing the task details, including:
            - id: The task's unique identifier.
            - description: The task's description.
            - agent_id: The ID of the agent associated with the task.
            - output: The task's response or output.
            - comment: Any comments associated with the task.
            - status: The current status of the task.
            - created_at: The timestamp when the task was created (as a string).
    """
    try:
        tasks = get_tasks_ctrl(db, id)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Task fetched",
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
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"data": {}, "error_msg": "Invalid request", "error": str(e)},
        )


@router.post("")
def create_task(
    tasks: CreateTaskSchema, request: Request, db: Session = Depends(get_db_session)
):
    """
    Create a new task, process it using a custom agent, and return the results.

    This function performs the following steps:
    1. Creates a new task based on the provided CreateTaskSchema.
    2. Retrieves the associated agent and its tools.
    3. Initializes a CustomAgent with the agent's details and task information.
    4. Executes the task using the CustomAgent.
    5. Processes the output, including CSV file creation if required.
    6. Updates the task with the results.
    7. Returns a JSON response with the task details and outputs.

    Args:
        tasks (CreateTaskSchema): The schema containing task creation details.
        request (Request): The incoming request object.

    Returns:
        JSONResponse: A response containing the task details, outputs, and any attachments.

    Raises:
        Potential exceptions from called functions are not explicitly handled in this function.
    """
    try:
        new_task = create_tasks_ctrl(db, tasks)
        agent = get_agents_ctrl(db, tasks.agent_id)[0]

        previous_output = []

        if tasks.include_previous_output:
            for task_id in tasks.previous_output:
                output = get_tasks_ctrl(db, task_id)
                previous_output.append(
                    {
                        "description": output.description,
                        "expected_output": output.expected_output,
                        "response": output.response,
                    }
                )
        prompt = get_desc_prompt(agent["goal"], tasks.description, previous_output)
        get_tools = agent["tools"]

        results = start_agent.delay(
            agent["role"],
            agent["backstory"],
            agent["goal"],
            get_tools,
            tasks.expected_output,
            prompt,
            tasks.is_csv,
            str(request.base_url),
            new_task.id,
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Task completed",
                "data": {"task_id": new_task.id},
                "error_msg": "",
                "error": "",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"data": {}, "error_msg": "Invalid request", "error": str(e)},
        )


@router.get("/download/{file_path:path}")
def download_file(file_path: str):
    """
    Handle file download requests for CSV and Markdown files.

    This function performs the following steps:
    1. Constructs the actual file path based on the provided file_path.
    2. Checks if the file exists.
    3. Determines the media type based on the file extension.
    4. Returns a FileResponse for the requested file.

    Args:
        file_path (str): The path of the file to be downloaded, relative to the 'static' directory.

    Returns:
        FileResponse: A response containing the file content, with appropriate headers for download.
    """
    try:
        actual_path = os.path.abspath("static/" + file_path)

        # Check if the file exists
        if not os.path.isfile(actual_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Determine the media type from the file extension
        file_extension = os.path.splitext(file_path)[-1].lower()
        if file_extension == ".csv":
            media_type = "text/csv"
        elif file_extension == ".md":
            media_type = "text/markdown"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        return FileResponse(
            path=actual_path,
            filename=os.path.basename(file_path),
            media_type=media_type,
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"data": {}, "error_msg": "Invalid request", "error": str(e)},
        )
