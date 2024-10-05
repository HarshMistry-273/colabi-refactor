from pydantic import BaseModel


class CreateToolSchema(BaseModel):
    name: str
    description: str


def get_task_id_desc_ser(tasks):
    task_dict = {}

    for task in tasks:
        task_dict.update({"id": task.id, "description": task.description})

    return task_dict


def get_task_ser(tools):
    tools_dict = {}

    if not isinstance(tools, list):
        tools = [tools]
    for tool in tools:
        tools_dict.update(
            {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "created_at": str(tool.created_at),
            }
        )

    return tools_dict
