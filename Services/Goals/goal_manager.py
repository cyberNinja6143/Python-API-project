from __future__ import annotations


# Manages goals for users, including creation, retrieval, updating, and deletion.

from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

from Services.Storage.storage_service import StorageService


class GoalManager:
    """Manage goals and milestones for users."""

    def __init__(self, storage_dir: Union[str, Path] = "."):
        self.storage = StorageService(storage_dir)

    def list_goals_for_user(self, user_id: str) -> List[Dict[str, str]]:
        """Return all goals for a specific user."""
        goals = self.storage.load_goals()
        return [goal for goal in goals if goal.get("user_id") == str(user_id)]

    def get_goal(self, goal_id: str, user_id: str) -> Optional[Dict[str, str]]:
        """Return a specific goal if it belongs to the user."""
        for goal in self.storage.load_goals():
            if goal.get("goal_id") == str(goal_id) and goal.get("user_id") == str(user_id):
                return goal
        return None

    def create_goal(self, user_id: str, description: str, deadline: str, iscomplete: bool = False) -> Dict[str, str]:
        """Create a new goal for a user."""
        goals = self.storage.load_goals()
        goal = {
            "goal_id": str(self._next_id(goals, "goal_id")),
            "user_id": str(user_id),
            "description": description,
            "deadline": deadline,
            "iscomplete": "True" if iscomplete else "False",
            "created_at": datetime.utcnow().isoformat(sep=" ", timespec="seconds"),
        }
        goals.append(goal)
        self.storage.save_goals(goals)
        return goal

    def update_goal(
        self,
        goal_id: str,
        user_id: str,
        description: Optional[str] = None,
        deadline: Optional[str] = None,
        iscomplete: Optional[bool] = None,
    ) -> Optional[Dict[str, str]]:
        """Update a goal and return the updated goal or None if not found."""
        goals = self.storage.load_goals()
        for index, goal in enumerate(goals):
            if goal.get("goal_id") != str(goal_id) or goal.get("user_id") != str(user_id):
                continue

            if description is not None:
                goal["description"] = description
            if deadline is not None:
                goal["deadline"] = deadline
            if iscomplete is not None:
                goal["iscomplete"] = "True" if iscomplete else "False"

            goals[index] = goal
            self.storage.save_goals(goals)
            return goal

        return None

    def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete a goal and return True if deleted, False if not found."""
        goals = self.storage.load_goals()
        filtered = [goal for goal in goals if not (goal.get("goal_id") == str(goal_id) and goal.get("user_id") == str(user_id))]
        if len(filtered) == len(goals):
            return False
        self.storage.save_goals(filtered)
        return True

    def list_milestones_for_goal(self, goal_id: str) -> List[Dict[str, str]]:
        """Return all milestones for a specific goal."""
        milestones = self.storage.load_milestones()
        return [ms for ms in milestones if ms.get("goal_id") == str(goal_id)]

    def goal_exists_for_user(self, goal_id: str, user_id: str) -> bool:
        """Check if a goal exists and belongs to the user."""
        return self.get_goal(goal_id, user_id) is not None

    def create_milestone(self, goal_id: str, user_id: str, description: str, deadline: str, iscomplete: bool = False) -> Dict[str, str]:
        """Create a new milestone for a goal."""
        milestones = self.storage.load_milestones()
        milestone = {
            "milestone_id": str(self._next_id(milestones, "milestone_id")),
            "goal_id": str(goal_id),
            "user_id": str(user_id),
            "description": description,
            "deadline": deadline,
            "iscomplete": "True" if iscomplete else "False",
            "created_at": datetime.utcnow().isoformat(sep=" ", timespec="seconds"),
        }
        milestones.append(milestone)
        self.storage.save_milestones(milestones)
        return milestone

    def get_milestone(self, milestone_id: str) -> Optional[Dict[str, str]]:
        """Return a specific milestone."""
        for ms in self.storage.load_milestones():
            if ms.get("milestone_id") == str(milestone_id):
                return ms
        return None

    def update_milestone(
        self,
        milestone_id: str,
        description: Optional[str] = None,
        deadline: Optional[str] = None,
        iscomplete: Optional[bool] = None,
    ) -> Optional[Dict[str, str]]:
        """Update a milestone and return the updated milestone or None if not found."""
        milestones = self.storage.load_milestones()
        for index, milestone in enumerate(milestones):
            if milestone.get("milestone_id") != str(milestone_id):
                continue

            if description is not None:
                milestone["description"] = description
            if deadline is not None:
                milestone["deadline"] = deadline
            if iscomplete is not None:
                milestone["iscomplete"] = "True" if iscomplete else "False"

            milestones[index] = milestone
            self.storage.save_milestones(milestones)
            return milestone

        return None

    def delete_milestone(self, milestone_id: str) -> bool:
        """Delete a milestone and return True if deleted, False if not found."""
        milestones = self.storage.load_milestones()
        filtered = [ms for ms in milestones if ms.get("milestone_id") != str(milestone_id)]
        if len(filtered) == len(milestones):
            return False
        self.storage.save_milestones(filtered)
        return True

    def milestone_belongs_to_user_goal(self, milestone_id: str, user_id: str) -> bool:
        """Check if a milestone belongs to a goal owned by the user."""
        milestone = self.get_milestone(milestone_id)
        if milestone is None:
            return False
        goal_id = milestone.get("goal_id")
        return self.goal_exists_for_user(goal_id, user_id)

    @staticmethod
    def _next_id(items: List[Dict[str, str]], field: str) -> int:
        max_id = 0
        for item in items:
            try:
                current_id = int(item.get(field, 0))
            except (TypeError, ValueError):
                current_id = 0
            if current_id > max_id:
                max_id = current_id
        return max_id + 1
