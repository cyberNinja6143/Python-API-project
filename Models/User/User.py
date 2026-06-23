from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """Pydantic `User` model with `created_at` timestamp.

    This preserves the previous `.to_dict()` compatibility for storage and callers.
    """

    user_id: str
    username: str
    password_hash: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(sep=" ", timespec="seconds"))

    def to_dict(self) -> dict:
        return self.dict()
