from __future__ import annotations


# Uses secrets module to generate secure random tokens and stores it in tokens.csv using storage_service.
# I would have used JWT but that requires an install so I went with the secrets module instead.
# JWT is better because it does not require writing to a db or csv.


import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Union

from Services.Storage.storage_service import StorageService
from Models.Token.Token import Token


class TokenGenerator:
    """Creates secure random tokens and persists them to tokens.csv."""

    DEFAULT_TOKEN_BYTES = 32
    DEFAULT_LIFETIME_DAYS = 30

    def __init__(self, storage_dir: Union[str, Path] = ".", token_bytes: int = DEFAULT_TOKEN_BYTES) -> None:
        if not isinstance(token_bytes, int) or token_bytes <= 0:
            raise ValueError("token_bytes must be a positive integer")

        self.storage = StorageService(storage_dir)
        self.token_bytes = token_bytes

    def generate_token(
        self,
        user_id: str,
        prefix: Optional[str] = None,
        lifetime_days: int = DEFAULT_LIFETIME_DAYS,
    ) -> str:
        """Generate a secure token, save it to tokens.csv for a user, and set expiry 30 days from now."""
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        if not isinstance(prefix, (str, type(None))):
            raise TypeError("prefix must be a string or None")
        if not isinstance(lifetime_days, int) or lifetime_days <= 0:
            raise ValueError("lifetime_days must be a positive integer")

        token = secrets.token_urlsafe(self.token_bytes)
        if prefix:
            token = f"{prefix.strip()}-{token}"

        expires_at = datetime.utcnow() + timedelta(days=lifetime_days)
        token_record = Token(token=token, user_id=user_id.strip(), expires_at=expires_at.isoformat(sep=" ", timespec="seconds"))

        # save Token model as dict; Token includes its own created_at
        self.storage.save_token(token_record.to_dict())
        return token
