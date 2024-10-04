from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from src.agents.controllers import get_agents_ctrl
from src.tasks.serializers import CreateTaskSchema
from src.tasks.controllers import get_tasks_ctrl, create_tasks_ctrl, update_task_ctrl
from src.crew_search_bot import CrewAgent
import pandas as pd

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
    # agent = agent[0]

    init_task = CrewAgent(
        role=agent["role"],
        backstory=agent["backstory"],
        goal=agent["goal"],
        expected_output=new_task.expected_output,
        required_csv=tasks.csv,
        csv_file_name=tasks.csv_file_name,
    )
    prompt = f"""Goal of the task: {agent['goal']}. Follow the instruction: {tasks.description}. Optimize the task by ensuring clarity, precision, and accuracy in the information gathered, while maintaining alignment with the specified goal. Focus on delivering concise insights that meet the task requirements effectively."""

    res = init_task.main(description=prompt)
    
    tasks_output = res.tasks_output
    comment_task_output = tasks_output[1].raw

    actual_agent_output = tasks_output[0]
    max_length = max(len(v) for v in actual_agent_output.json_dict.values())

    for key in actual_agent_output.json_dict.keys():
        actual_agent_output.json_dict[key] += [None] * (max_length - len(actual_agent_output.json_dict[key]))

    if tasks.csv:
        file_name, ext = init_task.csv_file_name.rsplit(".")
        pd.DataFrame(actual_agent_output.json_dict).to_csv(
            "static/" + file_name + "." + "csv", index=False
        )
    if init_task.csv_file_name:
        full_file_url = f"{request.base_url}download/{init_task.csv_file_name}"

    update_task_ctrl(new_task.id, res)
    return JSONResponse(
        content={
            "id": new_task.id,
            "description": new_task.description,
            "agent_id": new_task.agent_id,
            "expected_output": new_task.expected_output,
            "response": actual_agent_output.raw,
            "comment" : comment_task_output,
            "file_path": full_file_url,
        }
    )
