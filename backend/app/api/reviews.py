from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.review import Review
from backend.app.schemas.schemas import ReviewCreate, ReviewResponse, ReviewTransitionRequest
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser
from backend.app.services.review_service import ReviewService, ReviewPermissionException
from backend.app.services.cycle_service import ClosedCycleModificationException

router = APIRouter(prefix="/reviews", tags=["Performance Reviews"])


@router.get("", response_model=List[ReviewResponse])
def list_reviews(
    review_cycle_id: Optional[str] = None,
    employee_id: Optional[str] = None,
    stage: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(Review)
    if review_cycle_id:
        query = query.where(Review.review_cycle_id == review_cycle_id)
    if employee_id:
        query = query.where(Review.employee_id == employee_id)
    if stage:
        query = query.where(Review.stage == stage)

    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_or_recalculate_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = ReviewService(db)
    try:
        rev = svc.create_or_recalculate_review(
            review_id=payload.review_id,
            employee_id=payload.employee_id,
            review_cycle_id=payload.review_cycle_id,
            actor_id=current_user.employee_id
        )
        return rev
    except ClosedCycleModificationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    rev = db.execute(select(Review).where(Review.review_id == review_id)).scalar_one_or_none()
    if not rev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Review {review_id} not found")
    return rev


@router.post("/{review_id}/transition", response_model=ReviewResponse)
def transition_review_stage(
    review_id: str,
    payload: ReviewTransitionRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = ReviewService(db)
    try:
        rev = svc.transition_stage(
            review_id=review_id,
            target_stage=payload.target_stage,
            actor_id=current_user.employee_id,
            comments=payload.comments
        )
        return rev
    except ClosedCycleModificationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ReviewPermissionException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
