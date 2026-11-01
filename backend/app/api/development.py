from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.development_plan import DevelopmentPlan
from backend.app.schemas.schemas import DevelopmentPlanCreate, DevelopmentPlanResponse, PlanApprovalRequest
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser
from backend.app.services.devplan_service import DevelopmentPlanService

router = APIRouter(prefix="/development-plans", tags=["Development Plans"])


@router.get("", response_model=List[DevelopmentPlanResponse])
def list_development_plans(
    employee_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(DevelopmentPlan)
    if employee_id:
        query = query.where(DevelopmentPlan.employee_id == employee_id)
    if status:
        query = query.where(DevelopmentPlan.status == status)

    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()


@router.post("", response_model=DevelopmentPlanResponse, status_code=status.HTTP_201_CREATED)
def create_development_plan(
    payload: DevelopmentPlanCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = DevelopmentPlanService(db)
    try:
        plan = svc.create_plan(
            plan_id=payload.plan_id,
            employee_id=payload.employee_id,
            competency_id=payload.competency_id,
            current_level=payload.current_level,
            target_level=payload.target_level,
            recommended_action=payload.recommended_action,
            start_date=payload.start_date,
            target_completion_date=payload.target_completion_date,
            review_id=payload.review_id,
            learning_resources=payload.learning_resources
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{plan_id}/approve", response_model=DevelopmentPlanResponse)
def approve_development_plan(
    plan_id: str,
    payload: PlanApprovalRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = DevelopmentPlanService(db)
    try:
        svc.approve_plan(
            plan_id=plan_id,
            approver_id=current_user.employee_id,
            approval_role=payload.approval_role,
            decision=payload.decision,
            comments=payload.comments
        )
        plan = db.execute(select(DevelopmentPlan).where(DevelopmentPlan.plan_id == plan_id)).scalar_one_or_none()
        return plan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
