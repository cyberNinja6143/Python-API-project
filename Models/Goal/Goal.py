from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import uuid4

from Models.Goal.Milestone import Milestone


class Goal(Milestone):
    def __init__(
        self,
        user_id: str,
        description: str,
        deadline: date,
        iscomplete: bool = False,
        goal_id: Optional[str] = None,
        milestones: Optional[List[Milestone]] = None,
    ):
        chosen_goal_id = goal_id or str(uuid4())
        super().__init__(
            goal_id=chosen_goal_id,
            user_id=user_id,
            description=description,
            deadline=deadline,
            iscomplete=iscomplete,
            milestone_id=chosen_goal_id,
        )
        self.goal_id = self.milestone_id
        self.milestones = milestones or []

    def to_dict(self) -> dict:
        return {
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "description": self.description,
            "deadline": self.deadline.isoformat() if isinstance(self.deadline, date) else str(self.deadline),
            "iscomplete": self.iscomplete,
            "milestones": [m.to_dict() for m in self.milestones],
        }
