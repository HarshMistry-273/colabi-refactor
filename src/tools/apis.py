from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from database import get_db_session
from src.tools.controllers import create_tool_ctrl, get_tools_ctrl
from src.tools.serializers import CreateToolSchema
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("")
def get_tools(id: str = None, db: Session = Depends(get_db_session)):
    """
    Retrieve tools based on the provided ID or fetch all tools if no ID is given.

    This function interacts with the controller `get_tools_ctrl` to fetch tools.
    If an ID is provided, it fetches the tool with the matching ID, otherwise, it
    retrieves all tools. If an error occurs during the process, it returns a 500
    error response.

    Args:
        id (str, optional): The ID of the tool to be fetched. Defaults to None.

    Returns:
        JSONResponse: A response containing either the tools data or an error message.
    """
    try:
        tools = get_tools_ctrl(db, id)
        return JSONResponse(
            status_code=200,
            content={
                "message": "Tool fetched",
                "data": {"tools": tools},
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
def create_tools(tool: CreateToolSchema, db: Session = Depends(get_db_session)):
    """
    Create a new tool and return a JSON response.

    This function attempts to create a new tool using the provided
    `CreateToolSchema` object. It uses the `create_tool_ctrl` function to
    handle the actual creation. If successful, it returns a JSON response
    with the created tool data and a success message. If an error occurs
    during the process, it catches the exception and returns a 500 error
    response with the error message.

    Args:
        tool (CreateToolSchema): The schema containing tool details.

    Returns:
        JSONResponse: A JSON response containing the result of the creation,
        with either a success message and tool data or an error message.
    """
    try:
        new_tool = create_tool_ctrl(db, tool)
        return JSONResponse(
            status_code=200,
            content={
                "message": "Tool created",
                "data": {"tools": new_tool},
                "error_msg": "",
                "error": "",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"data": {}, "error_msg": "Invalid request", "error": str(e)},
        )
