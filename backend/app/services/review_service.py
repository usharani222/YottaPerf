from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.review import Review, ReviewHistory
from backend.app.models.review_cycle import ReviewCycle
from backend.app.models.goal import Goal
from backend.app.models.feedback import Feedback
from backend.app.models.employee import Employee
from backend.app.services.cycle_service import ReviewCycleService


class ReviewPermissionException(Exception):
    pass


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.cycle_service = ReviewCycleService(db)

    def calculate_review_scores(self, employee_id: str, review_cycle_id: str) -> Dict[str, Any]:
        """
        Reconciles review score strictly from source records:
        - Goal score (50% default)
        - Competency score (30% default)
        - Feedback score (20% default)
        """
        cycle = self.db.execute(
            select(ReviewCycle).where(ReviewCycle.cycle_id == review_cycle_id)
        ).scalar_one_or_none()
        if not cycle:
            raise ValueError(f"Review cycle {review_cycle_id} not found")

        # 1. Goal Score
        goals = self.db.execute(
            select(Goal).where(Goal.employee_id == employee_id, Goal.review_cycle_id == review_cycle_id)
        ).scalars().all()
        if goals:
            goal_score = round(sum(float(g.calculated_progress) for g in goals) / len(goals), 2)
        else:
            goal_score = 0.00

        # 2. Competency / Self / Manager Score
        feedbacks = self.db.execute(
            select(Feedback).where(Feedback.subject_employee_id == employee_id, Feedback.review_cycle_id == review_cycle_id)
        ).scalars().all()

        manager_and_self = [f for f in feedbacks if f.feedback_type in ("SELF", "MANAGER")]
        peer_feedbacks = [f for f in feedbacks if f.feedback_type == "PEER"]

        if manager_and_self:
            avg_comp_rating = sum(float(f.rating) for f in manager_and_self) / len(manager_and_self)
            competency_score = round((avg_comp_rating / 5.0) * 100.0, 2)
        else:
            competency_score = 70.00

        if peer_feedbacks:
            avg_peer_rating = sum(float(f.rating) for f in peer_feedbacks) / len(peer_feedbacks)
            feedback_score = round((avg_peer_rating / 5.0) * 100.0, 2)
        else:
            feedback_score = 70.00

        # Weighted calculation
        w_goal = float(cycle.goal_weight) / 100.0
        w_comp = float(cycle.competency_weight) / 100.0
        w_fb = float(cycle.feedback_weight) / 100.0

        final_score = round((goal_score * w_goal) + (competency_score * w_comp) + (feedback_score * w_fb), 2)

        if final_score >= 90.0:
            rating_cat = "OUTSTANDING"
        elif final_score >= 75.0:
            rating_cat = "EXCEEDS_EXPECTATIONS"
        elif final_score >= 60.0:
            rating_cat = "MEETS_EXPECTATIONS"
        else:
            rating_cat = "NEEDS_IMPROVEMENT"

        return {
            "goal_score": goal_score,
            "competency_score": competency_score,
            "feedback_score": feedback_score,
            "final_score": final_score,
            "rating_category": rating_cat
        }

    def create_or_recalculate_review(
        self,
        review_id: str,
        employee_id: str,
        review_cycle_id: str,
        actor_id: Optional[str] = None
    ) -> Review:
        self.cycle_service.validate_cycle_modification_allowed(review_cycle_id, actor_id=actor_id)

        scores = self.calculate_review_scores(employee_id, review_cycle_id)

        review = self.db.execute(
            select(Review).where(Review.employee_id == employee_id, Review.review_cycle_id == review_cycle_id)
        ).scalar_one_or_none()

        if not review:
            review = Review(
                review_id=review_id,
                employee_id=employee_id,
                review_cycle_id=review_cycle_id,
                stage="DRAFT",
                goal_score=scores["goal_score"],
                competency_score=scores["competency_score"],
                feedback_score=scores["feedback_score"],
                final_score=scores["final_score"],
                rating_category=scores["rating_category"]
            )
            self.db.add(review)
            self.db.flush()

            import uuid
            rh = ReviewHistory(
                history_id=f"RH-{uuid.uuid4().hex[:8].upper()}",
                review_id=review_id,
                previous_stage="NONE",
                new_stage="DRAFT",
                changed_by=actor_id or employee_id,
                comments="Initial performance review appraisal drafted."
            )
            self.db.add(rh)
        else:
            review.goal_score = scores["goal_score"]
            review.competency_score = scores["competency_score"]
            review.feedback_score = scores["feedback_score"]
            review.final_score = scores["final_score"]
            review.rating_category = scores["rating_category"]
            review.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(review)
        return review

    def transition_stage(
        self,
        review_id: str,
        target_stage: str,
        actor_id: str,
        comments: Optional[str] = None
    ) -> Review:
        review = self.db.execute(select(Review).where(Review.review_id == review_id)).scalar_one_or_none()
        if not review:
            raise ValueError(f"Review {review_id} not found")

        self.cycle_service.validate_cycle_modification_allowed(review.review_cycle_id, actor_id=actor_id)

        # Rule: Employees cannot approve or finalize their own review!
        if target_stage in ("APPROVED", "COMPLETED") and actor_id == review.employee_id:
            raise ReviewPermissionException("Security violation: Employees cannot approve their own performance review.")

        old_stage = review.stage
        review.stage = target_stage
        review.updated_at = datetime.now(timezone.utc)

        if target_stage == "SELF_REVIEW_PENDING":
            review.self_submitted_at = datetime.now(timezone.utc)
        elif target_stage == "HR_REVIEW_PENDING":
            review.manager_approved_at = datetime.now(timezone.utc)
        elif target_stage in ("APPROVED", "COMPLETED"):
            review.hr_approved_at = datetime.now(timezone.utc)

        import uuid
        rh = ReviewHistory(
            history_id=f"RH-{uuid.uuid4().hex[:8].upper()}",
            review_id=review_id,
            previous_stage=old_stage,
            new_stage=target_stage,
            changed_by=actor_id,
            comments=comments or f"Review transitioned to {target_stage}"
        )
        self.db.add(rh)
        self.db.commit()
        self.db.refresh(review)
        return review
