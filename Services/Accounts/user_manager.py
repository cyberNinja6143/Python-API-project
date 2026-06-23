from __future__ import annotations


# Uses storage_service class to CRUD the users csv file.
# Does not handle password hashing, that is done in password_hasher.
from Services.Accounts.password_hasher import PasswordHasher
from Services.Storage.storage_service import StorageService
from Models.User.User import User
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union


class UserManager:
    """A lightweight user manager for CSV-backed user storage."""

    def __init__(self, storage_dir: Union[str, Path] = "."):
        self.storage = StorageService(storage_dir)

    def list_users(self) -> List[Dict[str, str]]:
        """Return all users stored in the users CSV file."""
        return self.storage.load_users()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, str]]:
        """Return a user record by user_id or None if not found."""
        for user in self.list_users():
            if user.get("user_id") == str(user_id):
                return user
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, str]]:
        """Return a user record by username or None if not found."""
        normalized = self._normalize_username(username)
        for user in self.list_users():
            if self._normalize_username(user.get("username", "")) == normalized:
                return user
        return None

    def create_user(self, username: str, password: str) -> Dict[str, str]:
        """Create a new user and persist it to the users CSV file."""
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username must be a non-empty string")
        if not isinstance(password, str) or not password:
            raise ValueError("password must be a non-empty string")

        if self.get_user_by_username(username) is not None:
            raise ValueError("username already exists")

        users = self.list_users()
        user_id = str(self._next_user_id(users))
        password_hash = PasswordHasher.hash_password(password)
        # include created_at timestamp to track when the user was created
        new_user = User(user_id=user_id, username=username.strip(), password_hash=password_hash).to_dict()
        users.append(new_user)
        self.storage.save_users(users)
        return new_user

    def delete_user(self, user_id: str) -> bool:
        """Delete a user by user_id. Returns True when a user was removed."""
        users = self.list_users()
        filtered = [user for user in users if user.get("user_id") != str(user_id)]
        if len(filtered) == len(users):
            return False
        self.storage.save_users(filtered)
        return True

    @staticmethod
    def _normalize_username(username: str) -> str:
        return username.strip().lower()

    @staticmethod
    def _next_user_id(users: List[Dict[str, str]]) -> int:
        if not users:
            return 1
        max_id = 0
        for user in users:
            try:
                current_id = int(user.get("user_id", 0))
            except ValueError:
                current_id = 0
            if current_id > max_id:
                max_id = current_id
        return max_id + 1
