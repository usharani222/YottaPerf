from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.check_in import CheckIn
from backend.app.schemas.schemas import CheckInCreate, CheckInResponse
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser
from backend.app.services.checkin_service import CheckInService
from backend.app.services.cycle_service import ClosedCycleModificationException

router = APIRouter(prefix="/check-ins", tags=["Check-ins"])


@router.get("", response_model=List[CheckInResponse])
def list_check_ins(
    employee_id: Optional[str] = None,
    goal_id: Optional[str] = None,
    review_cycle_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(CheckIn)
    if employee_id:
        query = query.where(CheckIn.employee_id == employee_id)
    if goal_id:
        query = query.where(CheckIn.goal_id == goal_id)
    if review_cycle_id:
        query = query.where(CheckIn.review_cycle_id == review_cycle_id)

    query = query.order_by(CheckIn.check_in_date.desc()).offset(skip).limit(limit)
    return db.execute(query).scalars().all()


@router.post("", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def submit_check_in(
    payload: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = CheckInService(db)
    try:
        check_in = svc.create_check_in(
            check_in_id=payload.check_in_id,
            employee_id=payload.employee_id,
            goal_id=payload.goal_id,
            review_cycle_id=payload.review_cycle_id,
            check_in_date=payload.check_in_date,
            progress_update=payload.progress_update,
            employee_comments=payload.employee_comments,
            manager_comments=payload.manager_comments,
            blockers=payload.blockers,
            next_steps=payload.next_steps,
            evidence_reference_url=payload.evidence_reference_url,
            evidence_type=payload.evidence_type,
            evidence_description=payload.evidence_description
        )
        return check_in
    except ClosedCycleModificationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
