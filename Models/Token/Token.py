from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Pydantic `Token` schema. Kept `.to_dict()` for compatibility with storage layer."""

    token: str
    user_id: str
    expires_at: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(sep=" ", timespec="seconds"))

    def to_dict(self) -> dict:
        return self.dict()
