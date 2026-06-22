from __future__ import annotations


# looks through the tokens.csv file to see if the token is valid, and if it is expired or not using storage_service.

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from Services.Storage.storage_service import StorageService


class TokenValidator:
    """Validate tokens stored in tokens.csv and check expiration."""

    def __init__(self, storage_dir: Union[str, Path] = ".") -> None:
        self.storage = StorageService(storage_dir)

    def validate(self, token: str) -> bool:
        """Return True when the token exists and has not expired."""
        if not isinstance(token, str) or not token:
            return False

        for record in self.storage.load_tokens():
            if record.get("token") != token:
                continue

            expires_at = record.get("expires_at")
            expiry = self._parse_datetime(expires_at)
            if expiry is None:
                return False
            return datetime.utcnow() < expiry

        return False

    def get_user_id(self, token: str) -> Optional[str]:
        """Return the user_id associated with a valid token, or None if invalid."""
        if not self.validate(token):
            return None

        for record in self.storage.load_tokens():
            if record.get("token") == token:
                user_id = record.get("user_id")
                return user_id if isinstance(user_id, str) and user_id.strip() else None

        return None

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not isinstance(value, str) or not value:
            return None

        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

