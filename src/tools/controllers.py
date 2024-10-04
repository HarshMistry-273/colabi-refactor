from fastapi import HTTPException
from database import db
from models.model import Tool
from src.tools.serializers import get_task_id_desc_ser, get_task_ser


def create_tool_ctrl(tool):
    try:
        new_tool = Tool(
            name=tool.name, description=tool.description, agent_id=tool.agent_id
        )
        db.add(new_tool)
        db.commit()
        db.refresh()

        return get_task_id_desc_ser(new_tool)
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
