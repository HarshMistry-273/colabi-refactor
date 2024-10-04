from pydantic import BaseModel


class CreateToolSchema(BaseModel):
    name: str
    description: str
    agent_id: int


def get_task_id_desc_ser(tasks):
    task_dict = {}

    for task in tasks:
        task_dict.update({"id": task.id, "description": task.description})

    return task_dict


def get_task_ser(tasks):
    task_dict = {}

    for task in tasks:
        task_dict.update(
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "agent_id": task.agent_id,
                "created_at": task.created_at,
            }
        )

    return task_dict
