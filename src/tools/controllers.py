from fastapi import HTTPException
from database import db
from src.tools.models import Tool
from src.tools.serializers import get_task_id_desc_ser, get_task_ser


def create_tool_ctrl(tool: Tool):
    try:
        new_tool = Tool(
            name=tool.name, description=tool.description
        )
        db.add(new_tool)
        db.commit()
        db.refresh(new_tool)

        new_tool = get_task_ser(new_tool)
        return new_tool
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_tools_ctrl(id):
    try:
        if id:
            tools = db.query(Tool).filter(Tool.id == id).all()
        else:
            tools = db.query(Tool).all()
        tools = get_task_ser(tools)
        return tools
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_tools_by_agent_id(agent_id):
    try:
        tools = db.query(Tool).filter(Tool.agent_id == agent_id).all()

        return tools
    except Exception as e:
        raise HTTPException(status_code=500, details=str(e))