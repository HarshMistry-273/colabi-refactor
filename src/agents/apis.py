from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.agents.serializers import CreateAgentSchema
from src.agents.controllers import create_agent_ctrl, get_agents_ctrl

router = APIRouter()


@router.get("")
def get_agents(id: str = None):
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

        all_agents = get_agents_ctrl(id)
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
            status_code=500, content={"data": {}, "error_msg": "Invalid request", "error": str(e)}
        )


@router.post("")
def create_agent(agent: CreateAgentSchema):
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
        new_agent = create_agent_ctrl(agent)
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
            status_code=500, content={"data": {}, "error_msg": "Invalid request", "error": str(e)}
        )
