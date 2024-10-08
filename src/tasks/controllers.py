from fastapi import HTTPException
from src.tasks.models import Task
from datetime import datetime, UTC
from sqlalchemy.orm import Session


def create_tasks_ctrl(db: Session, task):
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


def get_tasks_ctrl(db: Session, id):
    try:
        if id:
            task = db.query(Task).filter(Task.id == id).first()
        else:
            task = db.query(Task).all()
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_task_ctrl(db: Session, id, res, comment, full_file_url):
    try:
        update = {
            "response": res,
            "comment": comment,
            "attachments": full_file_url,
            "completed_at": datetime.now(tz=UTC),
            "status": "completed",
        }
        task = db.query(Task).filter(Task.id == id).update(update)
        db.commit()

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
