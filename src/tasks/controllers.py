from fastapi import HTTPException
from database import db
from models.model import Task
from datetime import datetime, UTC


def create_tasks_ctrl(task):
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


def get_tasks_ctrl(id):
    try:
        if id:
            task = db.query(Task).filter(Task.id == id).first()
        else:
            task = db.query(Task).all()
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_task_ctrl(id, res):
    try:
        update = {
            "response": res,
            "completed_at": datetime.now(tz=UTC),
            "status": "completed",
        }
        task = db.query(Task).filter(Task.id == id).update(update)
        db.commit()

        return task

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
