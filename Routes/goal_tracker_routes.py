from datetime import datetime
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from Models.Request.goal_create_request import GoalCreateRequest
from Models.Request.goal_update_request import GoalUpdateRequest
from Models.Request.login_request import LoginRequest
from Models.Request.account_create_request import AccountCreateRequest
from Models.Request.milestone_create_request import MilestoneCreateRequest
from Models.Request.milestone_update_request import MilestoneUpdateRequest
from Models.Response.goal_response import GoalResponse
from Models.Response.login_response import LoginResponse
from Models.Response.milestone_response import MilestoneResponse
from Services.Accounts.Token.token_generator import TokenGenerator
from Services.Accounts.Token.token_validator import TokenValidator
from Services.Accounts.authentication_service import AuthenticationService
from Services.Goals.goal_manager import GoalManager
from Services.Storage.storage_service import StorageService


app = FastAPI(
    title="Goal Tracker API",
    description="Log personal goals with deadlines, milestones, and completion status.",
    version="1.0.0",
)

storage = StorageService()
auth_service = AuthenticationService()
token_generator = TokenGenerator()
token_validator = TokenValidator()
goal_manager = GoalManager()

authorization_scheme = APIKeyHeader(name="Authorization", description="Type 'Bearer <your_token>'")


def _parse_bool(value: Optional[bool]) -> bool:
    if isinstance(value, bool):
        return value
    return False


def _parse_deadline(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("deadline must be a non-empty ISO date string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("deadline must be a valid ISO date or datetime string") from exc
    return parsed.date().isoformat()


def _get_current_user_id(token: str = Security(authorization_scheme)) -> str:
    if not isinstance(token, str) or not token.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header must be Bearer <token>")
    token_value = token.split(" ", 1)[1]
    if not token_validator.validate(token_value):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = token_validator.get_user_id(token_value)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to resolve token user")
    return user_id


def _milestone_response(milestone: Dict[str, str]) -> MilestoneResponse:
    return MilestoneResponse(
        milestone_id=milestone.get("milestone_id", ""),
        goal_id=milestone.get("goal_id", ""),
        user_id=milestone.get("user_id", ""),
        description=milestone.get("description", ""),
        deadline=milestone.get("deadline", ""),
        iscomplete=milestone.get("iscomplete", "False") == "True",
    )


def _goal_response(goal: Dict[str, str]) -> GoalResponse:
    milestones = goal_manager.list_milestones_for_goal(goal.get("goal_id", ""))
    return GoalResponse(
        goal_id=goal.get("goal_id", ""),
        user_id=goal.get("user_id", ""),
        description=goal.get("description", ""),
        deadline=goal.get("deadline", ""),
        iscomplete=goal.get("iscomplete", "False") == "True",
        milestones=[_milestone_response(ms) for ms in milestones],
    )


@app.post("/accounts", status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreateRequest):
    try:
        user = auth_service.user_manager.create_user(payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {"user_id": user["user_id"], "username": user["username"]}


@app.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if not auth_service.authenticate(payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = auth_service.user_manager.get_user_by_username(payload.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = token_generator.generate_token(user_id=user["user_id"])
    return {"access_token": token, "token_type": "bearer"}


@app.get("/goals", response_model=List[GoalResponse])
def list_goals(user_id: str = Depends(_get_current_user_id)):
    goals = goal_manager.list_goals_for_user(user_id)
    return [_goal_response(goal) for goal in goals]


@app.post("/goals", response_model=GoalResponse)
def create_goal(payload: GoalCreateRequest, user_id: str = Depends(_get_current_user_id)):
    try:
        deadline_value = _parse_deadline(payload.deadline)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    goal = goal_manager.create_goal(
        user_id=user_id,
        description=payload.description.strip(),
        deadline=deadline_value,
        iscomplete=_parse_bool(payload.iscomplete),
    )
    return _goal_response(goal)


@app.get("/goals/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: str, user_id: str = Depends(_get_current_user_id)):
    goal = goal_manager.get_goal(goal_id, user_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return _goal_response(goal)


@app.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: str, payload: GoalUpdateRequest, user_id: str = Depends(_get_current_user_id)):
    deadline_value = None
    if payload.deadline is not None:
        try:
            deadline_value = _parse_deadline(payload.deadline)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if payload.description is not None and not payload.description.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="description must be a non-empty string")

    goal = goal_manager.update_goal(
        goal_id=goal_id,
        user_id=user_id,
        description=payload.description.strip() if payload.description else None,
        deadline=deadline_value,
        iscomplete=payload.iscomplete,
    )
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return _goal_response(goal)


@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: str, user_id: str = Depends(_get_current_user_id)):
    if not goal_manager.delete_goal(goal_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return {"detail": "Goal deleted"}


@app.get("/goals/{goal_id}/milestones", response_model=List[MilestoneResponse])
def list_milestones(goal_id: str, user_id: str = Depends(_get_current_user_id)):
    if not goal_manager.goal_exists_for_user(goal_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    milestones = goal_manager.list_milestones_for_goal(goal_id)
    return [_milestone_response(ms) for ms in milestones]


@app.post("/milestones", response_model=MilestoneResponse)
def create_milestone(payload: MilestoneCreateRequest, user_id: str = Depends(_get_current_user_id)):
    if not goal_manager.goal_exists_for_user(payload.goal_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    try:
        deadline_value = _parse_deadline(payload.deadline)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    milestone = goal_manager.create_milestone(
        goal_id=payload.goal_id,
        user_id=user_id,
        description=payload.description.strip(),
        deadline=deadline_value,
        iscomplete=_parse_bool(payload.iscomplete),
    )
    return _milestone_response(milestone)


@app.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(milestone_id: str, payload: MilestoneUpdateRequest, user_id: str = Depends(_get_current_user_id)):
    if not goal_manager.milestone_belongs_to_user_goal(milestone_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    deadline_value = None
    if payload.deadline is not None:
        try:
            deadline_value = _parse_deadline(payload.deadline)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if payload.description is not None and not payload.description.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="description must be a non-empty string")

    milestone = goal_manager.update_milestone(
        milestone_id=milestone_id,
        description=payload.description.strip() if payload.description else None,
        deadline=deadline_value,
        iscomplete=payload.iscomplete,
    )
    if milestone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return _milestone_response(milestone)


@app.delete("/milestones/{milestone_id}")
def delete_milestone(milestone_id: str, user_id: str = Depends(_get_current_user_id)):
    if not goal_manager.milestone_belongs_to_user_goal(milestone_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    if not goal_manager.delete_milestone(milestone_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return {"detail": "Milestone deleted"}


@app.get("/progress")
def progress(user_id: str = Depends(_get_current_user_id)):
    """Return progress for each goal belonging to the authenticated user.

    Progress is computed as: completed_milestones / total_milestones * 100.
    If a goal has no milestones the progress is 0. Results are returned as a list
    of objects with `goal_id`, `description`, `progress_percent`, `completed`, and `total`.
    """
    goals = goal_manager.list_goals_for_user(user_id)
    result = []
    for goal in goals:
        goal_id = goal.get("goal_id", "")
        milestones = goal_manager.list_milestones_for_goal(goal_id)
        total = len(milestones)
        if total == 0:
            progress_percent = 0.0
            completed = 0
        else:
            # Milestone `iscomplete` may be stored as string "True"/"False" or boolean
            completed = 0
            for m in milestones:
                val = m.get("iscomplete")
                if isinstance(val, bool):
                    if val:
                        completed += 1
                else:
                    if str(val).strip().lower() == "true":
                        completed += 1
            progress_percent = (completed / total) * 100.0

        result.append(
            {
                "goal_id": goal_id,
                "description": goal.get("description", ""),
                "progress_percent": round(progress_percent, 2),
                "completed": completed,
                "total": total,
            }
        )

    return result
