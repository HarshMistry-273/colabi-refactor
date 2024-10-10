import json
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from database import get_db_session
from src.agents.serializers import (
    CreateAgentSchema,
    UpdateCustomAgent,
)
from src.agents.controllers import AgentController
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("")
def get_agents(id: str = None, db: Session = Depends(get_db_session)):
    """
    Retrieve agents from the system, optionally filtered by ID.

    This function performs the following steps:
    1. Calls the get_agents_ctrl function with the provided ID (if any) to retrieve agent(s).
    2. If successful, returns a JSON response with the agent data.
    3. If an exception occurs, returns a JSON response with error information.

    Args:
        id (str, optional): The unique identifier of a specific agent to retrieve.
                            If None, all agents are retrieved. Defaults to None.

    Returns:
        JSONResponse: A response containing either:
            - On success (status code 200):
                - message: A success message.
                - data: A dictionary containing a list of agent(s) under the "agents" key.
                - error_msg: An empty string.
                - error: An empty string.
            - On failure (status code 500):
                - data: An empty dictionary.
                - error_msg: An empty string.
                - error: The string representation of the exception that occurred.
    """
    try:

        all_agents = AgentController.get_agents_ctrl(db, id)
        return JSONResponse(
            status_code=200,
            content={
                "message": "Agent created",
                "data": {"agents": all_agents},
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
def create_agent(agent: CreateAgentSchema, db: Session = Depends(get_db_session)):
    """
    Create a new agent in the system.

    This function performs the following steps:
    1. Receives agent data through the CreateAgentSchema.
    2. Calls the create_agent_ctrl function to create the new agent.
    3. If successful, returns a JSON response with the new agent data.
    4. If an exception occurs, returns a JSON response with error information.

    Args:
        agent (CreateAgentSchema): A Pydantic schema containing the necessary data to create a new agent.

    Returns:
        JSONResponse: A response containing either:
            - On success (status code 200):
                - message: A success message stating "Agent created".
                - data: A dictionary containing the new agent data under the "agents" key.
                - error_msg: An empty string.
                - error: An empty string.
            - On failure (status code 500):
                - data: An empty dictionary.
                - error_msg: An empty string.
                - error: The string representation of the exception that occurred.

    """
    try:
        new_agent = AgentController.create_agent_ctrl(db, agent)
        return JSONResponse(
            status_code=200,
            content={
                "message": "Agent created",
                "data": {"agents": new_agent},
                "error_msg": "",
                "error": "",
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"data": {}, "error_msg": "Invalid request", "error": str(e)},
        )


@router.post("/custom")
def create_custom_agent(
    name: str = Form(...),
    role: str = Form(...),
    goal: str = Form(...),
    backstory: str = Form(...),
    tools: Optional[str] = Form(...),
    payload: Optional[str] = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
):
    """
    Create a new agent in the system.

    This function performs the following steps:
    1. Receives agent data through the CreateCustomAgentSchema.
    2. Calls the create_custom_agent_ctrl function to create the new custom agent.
    3. If successful, returns a JSON response with the new agent data.
    4. If an exception occurs, returns a JSON response with error information.

    Args:
        agent (CreateAgentSchema): A Pydantic schema containing the necessary data to create a new agent.

    Returns:
        JSONResponse: A response containing either:
            - On success (status code 200):
                - message: A success message stating "Agent created".
                - data: A dictionary containing the new agent data under the "agents" key.
                - error_msg: An empty string.
                - error: An empty string.
            - On failure (status code 500):
                - data: An empty dictionary.
                - error_msg: An empty string.
                - error: The string representation of the exception that occurred.
    """
    try:
        new_custom_agent = AgentController.create_custom_agent_ctrl(
            db,
            name,
            role,
            goal,
            backstory,
            tools.replace('"', "").split(","),
            json.loads(payload),
            file,
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Custom Agent created",
                "data": {"agents": new_custom_agent},
                "error_msg": "",
                "error": "",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"data": {}, "error_msg": "Invalid request", "error": str(e)},
        )


# @router.put("/custom")
# def update_custom_agent(
#     id: str, update_agent: UpdateCustomAgent, db: Session = Depends(get_db_session)
# ):

#     agent = AgentController.update_custom_agent_ctrl(db, id, update_agent)
#     return JSONResponse(
#         status_code=200,
#         content={
#             "message": "Custom Agent updated",
#             "data": {"agents": agent},
#             "error_msg": "",
#             "error": "",
#         },
#     )
