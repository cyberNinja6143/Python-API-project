from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import uuid4


class Milestone:
    def __init__(
        self,
        goal_id: str,
        user_id: str,
        description: str,
        deadline: date,
        iscomplete: bool = False,
        milestone_id: Optional[str] = None,
    ):
        self.milestone_id = milestone_id or str(uuid4())
        self.goal_id = goal_id
        self.user_id = user_id
        self.description = description
        self.deadline = deadline
        self.iscomplete = iscomplete

    def to_dict(self) -> dict:
        return {
            "milestone_id": self.milestone_id,
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "description": self.description,
            "deadline": self.deadline.isoformat() if isinstance(self.deadline, date) else str(self.deadline),
            "iscomplete": self.iscomplete,
        }
