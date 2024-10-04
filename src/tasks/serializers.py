from pydantic import BaseModel, create_model
from typing import Optional


class CreateTaskSchema(BaseModel):
    description: str
    agent_id: str
    expected_output: str
    csv: Optional[bool] = False
    csv_file_name: Optional[str] = None
