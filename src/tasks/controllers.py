from fastapi import HTTPException
from src.tasks.models import Task
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


class TaskController:
    @staticmethod
    async def create_tasks_ctrl(db: Session, task):
        try:
            new_task = Task(
                description=task.description,
                agent_id=task.agent_id,
                expected_output=task.expected_output,
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            return new_task
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def async_create_tasks_ctrl(db: AsyncSession, task):
        try:
            new_task = Task(
                description=task.description,
                agent_id=task.agent_id,
                expected_output=task.expected_output,
            )
            db.add(new_task)
            await db.commit()
            await db.refresh(new_task)
            return new_task
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_tasks_ctrl(db: Session, id):
        try:
            if id:
                task = db.query(Task).filter(Task.id == id).first()
            else:
                task = db.query(Task).all()
            return task
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def async_get_tasks_ctrl(db: AsyncSession, id):
        try:
            if id:
                task = await db.query(Task).filter(Task.id == id).first()
            else:
                task = await db.query(Task).all()
            return task
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_task_ctrl(db: Session, id, res, comment, full_file_url):
        try:
            # def update_task(db, id, res, comment, full_file_url):
            task = db.query(Task).filter(Task.id == id).first()
            
            if not task:
                return {"error": "Task not found"}
            
            task.response = res
            task.comment = comment
            task.attachments = full_file_url
            task.status = "completed"
            
            db.commit()
            db.refresh(task)
            # Retrieve the updated task
            # updated_task = TaskController.get_tasks_ctrl(db, id=id)
    
            return task

        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=500, detail=str(e))
