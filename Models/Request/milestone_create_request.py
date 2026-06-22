from typing import Optional

from pydantic import BaseModel, Field


class MilestoneCreateRequest(BaseModel):
    goal_id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    deadline: str = Field(..., min_length=1)
    iscomplete: Optional[bool] = False
