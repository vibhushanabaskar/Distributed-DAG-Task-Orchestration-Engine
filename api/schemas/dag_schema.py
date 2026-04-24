from pydantic import BaseModel
from typing import List, Optional

class TaskSchema(BaseModel):
    id: str
    command: Optional[str] = None
    file_path: Optional[str] = None
    dependencies: List[str] = []

class DAGSchema(BaseModel):
    dag_id: str
    tasks: List[TaskSchema]
