from typing import List

from pydantic import BaseModel, Field

from Models.Response.milestone_response import MilestoneResponse


class GoalResponse(BaseModel):
    goal_id: str
    user_id: str
    description: str
    deadline: str
    iscomplete: bool
    milestones: List[MilestoneResponse] = Field(default_factory=list)
