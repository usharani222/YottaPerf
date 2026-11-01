from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.feedback import Feedback
from backend.app.models.competency import Competency
from backend.app.schemas.schemas import FeedbackCreate, FeedbackResponse, CompetencyResponse
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser
from backend.app.services.feedback_service import FeedbackService, InvalidReviewerException
from backend.app.services.cycle_service import ClosedCycleModificationException

router = APIRouter(tags=["Competencies & Feedback"])


@router.get("/competencies", response_model=List[CompetencyResponse])
def list_competencies(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(Competency).where(Competency.is_active == True)
    if category:
        query = query.where(Competency.category == category)
    return db.execute(query).scalars().all()


@router.get("/feedback", response_model=List[FeedbackResponse])
def list_feedback(
    subject_employee_id: Optional[str] = None,
    reviewer_employee_id: Optional[str] = None,
    review_cycle_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(Feedback)
    if subject_employee_id:
        query = query.where(Feedback.subject_employee_id == subject_employee_id)
    if reviewer_employee_id:
        query = query.where(Feedback.reviewer_employee_id == reviewer_employee_id)
    if review_cycle_id:
        query = query.where(Feedback.review_cycle_id == review_cycle_id)

    query = query.order_by(Feedback.submission_date.desc()).offset(skip).limit(limit)
    return db.execute(query).scalars().all()


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    svc = FeedbackService(db)
    try:
        fb = svc.submit_feedback(
            feedback_id=payload.feedback_id,
            subject_employee_id=payload.subject_employee_id,
            reviewer_employee_id=current_user.employee_id,
            review_cycle_id=payload.review_cycle_id,
            feedback_type=payload.feedback_type,
            competency_id=payload.competency_id,
            rating=payload.rating,
            comments=payload.comments,
            evidence_id=payload.evidence_id
        )
        return fb
    except ClosedCycleModificationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidReviewerException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
