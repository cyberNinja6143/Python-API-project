from __future__ import annotations


# Stores and retrieves data from the csv files
# There are three csv files: users (contains user_id, username and password hash),
# goals (contains goal_id, user_id, description: str, deadline: date, iscomplete: bool) and
# milestones (contains milestone_id, goal_id, description: str, deadline: date, iscomplete: bool)


import json
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
        # Use JSON files instead of CSV files for storage.
        # Keeping file names similar but with .json extension to avoid introducing new dependencies.
        self.users_json = self.storage_dir / "users.json"
        self.goals_json = self.storage_dir / "goals.json"
        self.milestones_json = self.storage_dir / "milestones.json"
        self.tokens_json = self.storage_dir / "tokens.json"
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        # Create JSON files with empty lists if they don't exist.
        for path in [
            self.users_json,
            self.goals_json,
            self.milestones_json,
            self.tokens_json,
        ]:
            if not path.exists():
                with path.open("w", encoding="utf-8") as jf:
                    json.dump([], jf)

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
    def _read_json(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            with path.open("r", encoding="utf-8") as jf:
                data = json.load(jf)
        except Exception:
            # If the file is malformed, treat as empty to avoid crashing other services.
            return []
        if not isinstance(data, list):
            return []
        return data

    def _prepare_row_for_write(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize common types to JSON-friendly strings for compatibility.

        - Dates are serialized as YYYY-MM-DD
        - `iscomplete` booleans are stored as "True"/"False" strings to remain compatible
          with existing consumers that expect string values.
        - `expires_at` datetimes are stored as ISO-format strings.
        """
        out: Dict[str, Any] = {}
        for k, v in row.items():
            if v is None:
                out[k] = v
                continue
            if k in {"deadline"}:
                try:
                    out[k] = self._serialize_date(v)
                except Exception:
                    out[k] = str(v)
                continue
            if k == "created_at":
                # store created_at as ISO datetime string
                if isinstance(v, (datetime, date)):
                    out[k] = v.isoformat(sep=" ", timespec="seconds")
                else:
                    out[k] = str(v)
                continue
            if k == "expires_at":
                if isinstance(v, (datetime, date)):
                    out[k] = v.isoformat(sep=" ", timespec="seconds")
                else:
                    out[k] = str(v)
                continue
            if k == "iscomplete":
                out[k] = self._serialize_bool(v)
                continue
            out[k] = v
        return out

    def _write_json(self, path: Path, rows: List[Dict[str, Any]]) -> None:
        serializable = [self._prepare_row_for_write(r) for r in rows]
        with path.open("w", encoding="utf-8") as jf:
            json.dump(serializable, jf, ensure_ascii=False, indent=2)

    def _append_json(self, path: Path, row: Dict[str, Any]) -> None:
        existing = self._read_json(path)
        existing.append(self._prepare_row_for_write(row))
        with path.open("w", encoding="utf-8") as jf:
            json.dump(existing, jf, ensure_ascii=False, indent=2)

    def load_users(self) -> List[Dict[str, str]]:
        """Return a list of user records from users.csv, each as a dict with keys: user_id, username, password_hash."""
        return self._read_json(self.users_json)

    def load_goals(self) -> List[Dict[str, str]]:
        """Return a list of goal records from goals.csv, each as a dict with keys: goal_id, user_id, description, deadline, iscomplete."""
        return self._read_json(self.goals_json)

    def load_milestones(self) -> List[Dict[str, str]]:
        """Return a list of milestone records from milestones.csv, each as a dict with keys: milestone_id, goal_id, description, deadline, iscomplete."""
        return self._read_json(self.milestones_json)

    def load_tokens(self) -> List[Dict[str, str]]:
        """Return a list of token records from tokens.csv, each as a dict with keys: token, user_id, expires_at."""
        return self._read_json(self.tokens_json)

    def save_token(self, token: Dict[str, Any]) -> None:
        """Append a single token record to tokens.csv."""
        self._append_json(self.tokens_json, token)

    def save_users(self, users: List[Dict[str, Any]]) -> None:
        """Save a list of user records to users.csv, each dict should have keys: user_id, username, password_hash."""
        self._write_json(self.users_json, users)

    def save_goals(self, goals: List[Dict[str, Any]]) -> None:
        """Save a list of goal records to goals.csv, each dict should have keys: goal_id, user_id, description, deadline, iscomplete."""
        self._write_json(self.goals_json, goals)

    def save_milestones(self, milestones: List[Dict[str, Any]]) -> None:
        """Save a list of milestone records to milestones.csv, each dict should have keys: milestone_id, goal_id, description, deadline, iscomplete."""
        self._write_json(self.milestones_json, milestones)