from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from Models.Goal.Milestone import Milestone


class Goal(BaseModel):
    """Pydantic model for Goal, including a list of `Milestone`s and a `created_at` timestamp."""

    goal_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    description: str
    deadline: Union[date, str]
    iscomplete: bool = False
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(sep=" ", timespec="seconds"))
    milestones: List[Milestone] = Field(default_factory=list)

    def to_dict(self) -> dict:
        deadline = self.deadline
        if isinstance(deadline, date):
            deadline = deadline.isoformat()
        return {
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "description": self.description,
            "deadline": deadline,
            "iscomplete": self.iscomplete,
            "created_at": self.created_at,
            "milestones": [m.to_dict() for m in self.milestones],
        }
