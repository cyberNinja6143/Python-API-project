from __future__ import annotations


# Stores and retrieves data from the csv files
# There are three csv files: users (contains user_id, username and password hash),
# goals (contains goal_id, user_id, description: str, deadline: date, iscomplete: bool) and
# milestones (contains milestone_id, goal_id, description: str, deadline: date, iscomplete: bool)


import csv
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class StorageService:
    """Handles CRUD operations for the three csv files: users.csv, goals.csv and milestones.csv."""

    USER_FIELDS = ["user_id", "username", "password_hash"]
    GOAL_FIELDS = ["goal_id", "user_id", "description", "deadline", "iscomplete"]
    MILESTONE_FIELDS = ["milestone_id", "goal_id", "user_id", "description", "deadline", "iscomplete"]
    TOKEN_FIELDS = ["token", "user_id", "expires_at"]
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, storage_dir: Union[str, Path] = "."):
        self.storage_dir = Path(storage_dir)
        if str(self.storage_dir) == ".":
            self.storage_dir = Path(__file__).resolve().parent
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.users_csv = self.storage_dir / "users.csv"
        self.goals_csv = self.storage_dir / "goals.csv"
        self.milestones_csv = self.storage_dir / "milestones.csv"
        self.tokens_csv = self.storage_dir / "tokens.csv"
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        for path, headers in [
            (self.users_csv, self.USER_FIELDS),
            (self.goals_csv, self.GOAL_FIELDS),
            (self.milestones_csv, self.MILESTONE_FIELDS),
            (self.tokens_csv, self.TOKEN_FIELDS),
        ]:
            if not path.exists():
                with path.open("w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=headers)
                    writer.writeheader()

    @staticmethod
    def _serialize_date(value: Union[date, str]) -> str:
        if isinstance(value, date):
            return value.strftime(StorageService.DATE_FORMAT)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError:
                parsed = datetime.strptime(value, StorageService.DATE_FORMAT)
            return parsed.date().strftime(StorageService.DATE_FORMAT)
        raise ValueError("deadline must be a date or ISO-formatted string")

    @staticmethod
    def _serialize_bool(value: Union[bool, str]) -> str:
        if isinstance(value, bool):
            return "True" if value else "False"
        normalized = str(value).strip().lower()
        return "True" if normalized in {"true", "1", "yes", "y"} else "False"

    @staticmethod
    def _deserialize_bool(value: str) -> bool:
        return str(value).strip().lower() in {"true", "1", "yes", "y"}

    def _read_csv(self, path: Path, fields: List[str]) -> List[Dict[str, str]]:
        if not path.exists():
            return []
        with path.open("r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=fields)
            rows = list(reader)
        if rows and rows[0] == {field: field for field in fields}:
            return rows[1:]
        return rows

    def _write_csv(self, path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def _append_csv(self, path: Path, row: Dict[str, Any], fields: List[str]) -> None:
        file_exists = path.exists() and path.stat().st_size > 0
        with path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def load_users(self) -> List[Dict[str, str]]:
        """Return a list of user records from users.csv, each as a dict with keys: user_id, username, password_hash."""
        return self._read_csv(self.users_csv, self.USER_FIELDS)

    def load_goals(self) -> List[Dict[str, str]]:
        """Return a list of goal records from goals.csv, each as a dict with keys: goal_id, user_id, description, deadline, iscomplete."""
        return self._read_csv(self.goals_csv, self.GOAL_FIELDS)

    def load_milestones(self) -> List[Dict[str, str]]:
        """Return a list of milestone records from milestones.csv, each as a dict with keys: milestone_id, goal_id, description, deadline, iscomplete."""
        return self._read_csv(self.milestones_csv, self.MILESTONE_FIELDS)

    def load_tokens(self) -> List[Dict[str, str]]:
        """Return a list of token records from tokens.csv, each as a dict with keys: token, user_id, expires_at."""
        return self._read_csv(self.tokens_csv, self.TOKEN_FIELDS)

    def save_token(self, token: Dict[str, Any]) -> None:
        """Append a single token record to tokens.csv."""
        self._append_csv(self.tokens_csv, token, self.TOKEN_FIELDS)

    def save_users(self, users: List[Dict[str, Any]]) -> None:
        """Save a list of user records to users.csv, each dict should have keys: user_id, username, password_hash."""
        self._write_csv(self.users_csv, users, self.USER_FIELDS)

    def save_goals(self, goals: List[Dict[str, Any]]) -> None:
        """Save a list of goal records to goals.csv, each dict should have keys: goal_id, user_id, description, deadline, iscomplete."""
        self._write_csv(self.goals_csv, goals, self.GOAL_FIELDS)

    def save_milestones(self, milestones: List[Dict[str, Any]]) -> None:
        """Save a list of milestone records to milestones.csv, each dict should have keys: milestone_id, goal_id, description, deadline, iscomplete."""
        self._write_csv(self.milestones_csv, milestones, self.MILESTONE_FIELDS)