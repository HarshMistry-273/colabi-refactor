from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.agents.controllers import get_agents_ctrl
from src.crew_agents.custom_agents import CustomAgent
from src.crew_agents.prompts import get_desc_prompt
from src.tasks.serializers import CreateTaskSchema
from src.tasks.controllers import get_tasks_ctrl, create_tasks_ctrl, update_task_ctrl

# from src.crew_search_bot import CrewAgent

import pandas as pd

from src.utils.utils import get_uuid

router = APIRouter()


@router.get("")
def get_task(id: int):
    tasks = get_tasks_ctrl(id)

    return JSONResponse(
        content={
            "id": tasks.id,
            "description": tasks.description,
            "agent_id": tasks.agent_id,
            "created_at": str(tasks.created_at),
        }
    )


@router.post("")
def create_task(tasks: CreateTaskSchema, request: Request):
    new_task = create_tasks_ctrl(tasks)
    agent = get_agents_ctrl(tasks.agent_id)[0]
    prompt = get_desc_prompt(agent["goal"], tasks.description)

    init_task = CustomAgent(
        role=agent["role"],
        backstory=agent["backstory"],
        goal=agent["goal"],
        tools=[],
        expected_output=new_task.expected_output,
        description=prompt,
    )

    custom_task_output, comment_task_output = init_task.main()

    max_length = max(len(v) for v in custom_task_output.json_dict.values())

    for key in custom_task_output.json_dict.keys():
        custom_task_output.json_dict[key] += [None] * (
            max_length - len(custom_task_output.json_dict[key])
        )

    full_file_url = None
    if tasks.is_csv:
        file_name = f"{get_uuid()}.csv"
        pd.DataFrame(custom_task_output.json_dict).to_csv(
            "static/" + file_name, index=False
        )
        full_file_url = f"{request.base_url}static/{file_name}"

    update_task_ctrl(new_task.id, custom_task_output.raw)
    return JSONResponse(
        content={
            "id": new_task.id,
            "description": new_task.description,
            "agent_id": new_task.agent_id,
            "expected_output": new_task.expected_output,
            "response": custom_task_output.raw,
            "comment": comment_task_output.raw,
            "file_path": full_file_url,
        }
    )
