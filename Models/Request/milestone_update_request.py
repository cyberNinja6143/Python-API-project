from typing import Optional

from pydantic import BaseModel


class MilestoneUpdateRequest(BaseModel):
    description: Optional[str] = None
    deadline: Optional[str] = None
    iscomplete: Optional[bool] = None
