from typing import Optional

from pydantic import BaseModel, Field


class GoalCreateRequest(BaseModel):
    description: str = Field(..., min_length=1)
    deadline: str = Field(..., min_length=1)
    iscomplete: Optional[bool] = False
