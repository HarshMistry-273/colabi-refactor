from pydantic import BaseModel
from typing import Optional


class CreateTaskSchema(BaseModel):
    description: str
    agent_id: str
    expected_output: str
    is_csv: Optional[bool] = False
