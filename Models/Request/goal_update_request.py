from typing import Optional

from pydantic import BaseModel


class GoalUpdateRequest(BaseModel):
    description: Optional[str] = None
    deadline: Optional[str] = None
    iscomplete: Optional[bool] = None
