from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.goal import Goal, KeyResult, GoalHistory
from backend.app.schemas.schemas import (
    GoalCreate, GoalResponse, KeyResultCreate, KeyResultUpdate,
    KeyResultResponse, GoalHistoryResponse
)
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser
from backend.app.services.goal_service import GoalService, InvalidProgressException
from backend.app.services.cycle_service import ClosedCycleModificationException

router = APIRouter(tags=["Goals & Key Results"])


@router.get("/goals", response_model=List[GoalResponse])
def list_goals(
    employee_id: Optional[str] = None,
    review_cycle_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(Goal)
    if employee_id:
        query = query.where(Goal.employee_id == employee_id)
    if review_cycle_id:
        query = query.where(Goal.review_cycle_id == review_cycle_id)
    if status:
        query = query.where(Goal.status == status)

    query = query.offset(skip).limit(limit)
    goals = db.execute(query).scalars().all()
    return goals


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = GoalService(db)
    try:
        goal = svc.create_goal(
            goal_id=payload.goal_id,
            employee_id=payload.employee_id,
            review_cycle_id=payload.review_cycle_id,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            priority=payload.priority,
            start_date=payload.start_date,
            due_date=payload.due_date,
            weight=payload.weight,
            created_by=current_user.employee_id,
            is_admin_correction=payload.is_admin_correction,
            correction_reason=payload.correction_reason
        )
        return goal
    except ClosedCycleModificationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/goals/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    goal = db.execute(select(Goal).where(Goal.goal_id == goal_id)).scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Goal {goal_id} not found")
    return goal


@router.get("/goals/{goal_id}/history", response_model=List[GoalHistoryResponse])
def get_goal_history(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    history = db.execute(
        select(GoalHistory).where(GoalHistory.goal_id == goal_id).order_by(GoalHistory.version_number.asc())
    ).scalars().all()
    return history


@router.post("/goals/{goal_id}/key-results", response_model=KeyResultResponse, status_code=status.HTTP_201_CREATED)
def add_key_result(
    goal_id: str,
    payload: KeyResultCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = GoalService(db)
    try:
        kr = svc.add_key_result(
            key_result_id=payload.key_result_id,
            goal_id=goal_id,
            metric_name=payload.metric_name,
            baseline_value=payload.baseline_value,
            target_value=payload.target_value,
            current_value=payload.current_value,
            unit=payload.unit,
            metric_direction=payload.metric_direction,
            weight=payload.weight,
            actor_id=current_user.employee_id
        )
        return kr
    except ClosedCycleModificationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidProgressException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/key-results/{key_result_id}", response_model=KeyResultResponse)
def update_key_result(
    key_result_id: str,
    payload: KeyResultUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = GoalService(db)
    try:
        kr = svc.update_key_result_value(
            key_result_id=key_result_id,
            current_value=payload.current_value,
            actor_id=current_user.employee_id
        )
        return kr
    except ClosedCycleModificationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidProgressException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
