from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class Milestone(BaseModel):
    """Pydantic model for milestones. Keeps `to_dict()` for compatibility with storage and responses."""

    milestone_id: str = Field(default_factory=lambda: str(uuid4()))
    goal_id: str
    user_id: str
    description: str
    deadline: Union[date, str]
    iscomplete: bool = False
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(sep=" ", timespec="seconds"))

    def to_dict(self) -> dict:
        deadline = self.deadline
        if isinstance(deadline, date):
            deadline = deadline.isoformat()
        return {
            "milestone_id": self.milestone_id,
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "description": self.description,
            "deadline": deadline,
            "iscomplete": self.iscomplete,
            "created_at": self.created_at,
        }
