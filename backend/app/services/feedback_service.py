from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.models.feedback import Feedback, FeedbackEvidence, ReviewPermission
from backend.app.models.employee import Employee
from backend.app.models.competency import Competency
from backend.app.services.cycle_service import ReviewCycleService


class InvalidReviewerException(Exception):
    pass


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db
        self.cycle_service = ReviewCycleService(db)

    def validate_reviewer_relationship(
        self,
        subject_id: str,
        reviewer_id: str,
        feedback_type: str,
        review_cycle_id: str
    ) -> bool:
        """
        Validates legitimate organizational relationship:
        1. SELF: subject == reviewer
        2. MANAGER: reviewer is direct manager of subject
        3. PEER: shares department, OR shares manager, OR has explicit review_permissions entry
        """
        if feedback_type == "SELF":
            return subject_id == reviewer_id

        subj = self.db.execute(select(Employee).where(Employee.employee_id == subject_id)).scalar_one_or_none()
        rev = self.db.execute(select(Employee).where(Employee.employee_id == reviewer_id)).scalar_one_or_none()
        if not subj or not rev:
            return False

        if feedback_type == "MANAGER":
            return subj.manager_id == reviewer_id

        if feedback_type == "PEER":
            # Direct peer (same department)
            if subj.department == rev.department:
                return True
            # Same manager
            if subj.manager_id and subj.manager_id == rev.manager_id:
                return True
            # Cross-functional permission grant
            perm = self.db.execute(
                select(ReviewPermission).where(
                    ReviewPermission.review_cycle_id == review_cycle_id,
                    ReviewPermission.subject_employee_id == subject_id,
                    ReviewPermission.reviewer_employee_id == reviewer_id
                )
            ).scalar_one_or_none()
            if perm:
                return True

        return False

    def submit_feedback(
        self,
        feedback_id: str,
        subject_employee_id: str,
        reviewer_employee_id: str,
        review_cycle_id: str,
        feedback_type: str,
        competency_id: str,
        rating: float,
        comments: str,
        submission_date: Optional[date] = None,
        evidence_id: Optional[str] = None
    ) -> Feedback:
        self.cycle_service.validate_cycle_modification_allowed(review_cycle_id, actor_id=reviewer_employee_id)

        if rating < 1.0 or rating > 5.0:
            raise ValueError("Feedback rating must be between 1.00 and 5.00")

        # Reviewer eligibility validation
        is_valid = self.validate_reviewer_relationship(
            subject_employee_id, reviewer_employee_id, feedback_type, review_cycle_id
        )
        if not is_valid:
            raise InvalidReviewerException(
                f"Reviewer {reviewer_employee_id} does not have a legitimate relationship to {subject_employee_id} for {feedback_type} feedback."
            )

        feedback = Feedback(
            feedback_id=feedback_id,
            subject_employee_id=subject_employee_id,
            reviewer_employee_id=reviewer_employee_id,
            review_cycle_id=review_cycle_id,
            feedback_type=feedback_type,
            competency_id=competency_id,
            rating=round(rating, 2),
            comments=comments,
            submission_date=submission_date or date.today(),
            status="SUBMITTED"
        )
        self.db.add(feedback)
        self.db.flush()

        if evidence_id:
            fe = FeedbackEvidence(feedback_id=feedback_id, evidence_id=evidence_id)
            self.db.add(fe)

        self.db.commit()
        self.db.refresh(feedback)
        return feedback
