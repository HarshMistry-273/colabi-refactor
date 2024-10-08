from database import get_db_session_celery
from src.crew_agents.custom_agents import CustomAgent
from src.tasks.controllers import update_task_ctrl
from src.tools.controllers import get_tools_ctrl
from src.utils.utils import get_uuid
import pandas as pd
from src.crew_agents.custom_tools import mapping
from src.celery_worker import celery_app


@celery_app.task()
def start_agent(
    role,
    backstory,
    goal,
    get_tools,
    expected_output,
    prompt,
    is_csv,
    base_url,
    task_id,
):
    with get_db_session_celery() as db:

        # db = get_db_session()
        tools = []
        for tool in get_tools:
            agent_tool = get_tools_ctrl(db, tool)
            tools.append(mapping[agent_tool[0]["name"]])
        init_task = CustomAgent(
            role=role,
            backstory=backstory,
            goal=goal,
            tools=tools,
            expected_output=expected_output,
            description=prompt,
        )

        custom_task_output, comment_task_output = init_task.main()
        max_length = max(len(v) for v in custom_task_output.json_dict.values())

        # Handle the edge cases in which if we do get empty column
        for key in custom_task_output.json_dict.keys():
            custom_task_output.json_dict[key] += [None] * (
                max_length - len(custom_task_output.json_dict[key])
            )

        full_file_url = None
        if is_csv:
            file_name = f"{get_uuid()}.csv"
            pd.DataFrame(custom_task_output.json_dict).to_csv(
                "static/" + file_name, index=False
            )
            full_file_url = f"{base_url}api/v1/tasks/download/{file_name}"
        update_task_ctrl(
            db, task_id, custom_task_output.raw, comment_task_output.raw, full_file_url
        )
        return "Task Completed"
