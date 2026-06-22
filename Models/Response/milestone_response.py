from pydantic import BaseModel


class MilestoneResponse(BaseModel):
    milestone_id: str
    goal_id: str
    user_id: str
    description: str
    deadline: str
    iscomplete: bool
