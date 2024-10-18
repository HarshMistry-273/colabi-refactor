from fastapi import HTTPException
from src.tools.models import Tool
from src.tools.serializers import get_task_ser
from sqlalchemy.orm import Session

class ToolController:
    @staticmethod
    async def create_tool_ctrl(db: Session, tool: Tool):
        try:
            new_tool = Tool(name=tool.name, description=tool.description)
            db.add(new_tool)
            db.commit()
            db.refresh(new_tool)

            new_tool = get_task_ser(new_tool)
            return new_tool
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_tools_ctrl(db: Session, id):
        try:
            if id:
                tools = db.query(Tool).filter(Tool.id == id).all()
            else:
                tools = db.query(Tool).all()
            tools = get_task_ser(tools)
            return tools
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_tools_by_agent_id(db: Session, agent_id):
        try:
            tools = db.query(Tool).filter(Tool.agent_id == agent_id).all()

            return tools
        except Exception as e:
            raise HTTPException(status_code=500, details=str(e))
