from pydantic import BaseModel
from typing import Optional


class CreateTaskSchema(BaseModel):
    description: str
    agent_id: str
    expected_output: str
    include_previous_output: Optional[bool] = False
    previous_output: Optional[list[str]]
    is_csv: Optional[bool] = False
