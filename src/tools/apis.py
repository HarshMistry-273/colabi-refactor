import logging.config
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from database import get_db_session
from src.tools.controllers import ToolController
from src.tools.serializers import CreateToolSchema
from sqlalchemy.orm import Session
from src.utils.log import logger_set
import logging

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

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
        logger.info("Tool listing endpoint")
        tools = ToolController.get_tools_ctrl(db, id)
        logger_set.info(f"Tools listed")

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
        logger_set.error(f"Error getting tool : {e}")
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
        logger.info("Tool creation endpoint")
        new_tool = ToolController.create_tool_ctrl(db, tool)
        logger_set.info(f"Tool created, Tool id : {tool["id"]}")
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
        logger_set.error(f"Error creating tool : {e}")
        return JSONResponse(
            status_code=500,
            content={"data": {}, "error_msg": "Invalid request", "error": str(e)},
        )
