from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.review_cycle import ReviewCycle
from backend.app.schemas.schemas import ReviewCycleCreate, ReviewCycleResponse, CycleStageUpdateRequest
from backend.app.permissions.rbac import get_current_user, require_roles, AuthenticatedUser
from backend.app.services.cycle_service import ReviewCycleService

router = APIRouter(prefix="/review-cycles", tags=["Review Cycles"])


@router.get("", response_model=List[ReviewCycleResponse])
def list_review_cycles(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    cycles = db.execute(select(ReviewCycle).order_by(ReviewCycle.start_date.desc())).scalars().all()
    return cycles


@router.post("", response_model=ReviewCycleResponse, status_code=status.HTTP_201_CREATED)
def create_review_cycle(
    payload: ReviewCycleCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles(["ADMIN", "HR_PARTNER"]))
):
    svc = ReviewCycleService(db)
    try:
        cycle = svc.create_cycle(
            cycle_id=payload.cycle_id,
            cycle_name=payload.cycle_name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            submission_deadline=payload.submission_deadline,
            goal_weight=payload.goal_weight,
            competency_weight=payload.competency_weight,
            feedback_weight=payload.feedback_weight,
            actor_id=current_user.employee_id
        )
        return cycle
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{cycle_id}/stage", response_model=ReviewCycleResponse)
def update_cycle_stage(
    cycle_id: str,
    payload: CycleStageUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles(["ADMIN", "HR_PARTNER"]))
):
    svc = ReviewCycleService(db)
    try:
        cycle = svc.update_stage(
            cycle_id=cycle_id,
            new_stage=payload.stage,
            actor_id=current_user.employee_id,
            reason=payload.reason
        )
        return cycle
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
