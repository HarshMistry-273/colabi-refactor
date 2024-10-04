from fastapi import APIRouter
from src.tools.controllers import create_tool_ctrl, get_tools_ctrl
from src.tools.serializers import CreateToolSchema

router = APIRouter()


@router.get("")
def get_tools(id: int = None):
    tools = get_tools_ctrl(id)
    return {"message": "Tools fetched", "tools": tools}


@router.post("")
def create_tools(tool: CreateToolSchema):
    new_tool = create_tool_ctrl(tool)
    return {"message": "Tool created", "tools": new_tool}
