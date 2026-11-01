from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.review_cycle import ReviewCycle
from backend.app.models.audit import AuditEvent


class ClosedCycleModificationException(Exception):
    pass


class ReviewCycleService:
    def __init__(self, db: Session):
        self.db = db

    def create_cycle(
        self,
        cycle_id: str,
        cycle_name: str,
        start_date: date,
        end_date: date,
        submission_deadline: date,
        goal_weight: float = 50.0,
        competency_weight: float = 30.0,
        feedback_weight: float = 20.0,
        actor_id: Optional[str] = None
    ) -> ReviewCycle:
        if end_date <= start_date:
            raise ValueError("Cycle end_date must be greater than start_date")
        if round(goal_weight + competency_weight + feedback_weight, 2) != 100.0:
            raise ValueError("Cycle weights must sum to exactly 100.00%")

        cycle = ReviewCycle(
            cycle_id=cycle_id,
            cycle_name=cycle_name,
            start_date=start_date,
            end_date=end_date,
            submission_deadline=submission_deadline,
            stage="UPCOMING",
            goal_weight=goal_weight,
            competency_weight=competency_weight,
            feedback_weight=feedback_weight
        )
        self.db.add(cycle)

        import uuid
        audit = AuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            actor_id=actor_id,
            entity_name="REVIEW_CYCLE",
            entity_id=cycle_id,
            operation_type="CREATE",
            new_values={"cycle_name": cycle_name, "stage": "UPCOMING"},
            review_cycle_id=cycle_id,
            reason="Review cycle created"
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def update_stage(
        self,
        cycle_id: str,
        new_stage: str,
        actor_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> ReviewCycle:
        cycle = self.db.execute(
            select(ReviewCycle).where(ReviewCycle.cycle_id == cycle_id)
        ).scalar_one_or_none()
        if not cycle:
            raise ValueError(f"Review cycle {cycle_id} not found")

        valid_stages = ["UPCOMING", "OPEN", "EVALUATION", "CLOSED", "ARCHIVED"]
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage {new_stage}. Must be one of {valid_stages}")

        old_stage = cycle.stage
        cycle.stage = new_stage
        cycle.updated_at = datetime.now(timezone.utc)

        import uuid
        audit = AuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            actor_id=actor_id,
            entity_name="REVIEW_CYCLE",
            entity_id=cycle_id,
            operation_type="TRANSITION",
            old_values={"stage": old_stage},
            new_values={"stage": new_stage},
            review_cycle_id=cycle_id,
            reason=reason or f"Cycle stage changed to {new_stage}"
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def validate_cycle_modification_allowed(
        self,
        cycle_id: str,
        is_administrative_correction: bool = False,
        correction_reason: Optional[str] = None,
        actor_id: Optional[str] = None
    ):
        """
        Enforces closed cycle immutability.
        Raises ClosedCycleModificationException if the cycle is CLOSED or ARCHIVED
        unless it is an explicit administrative correction with reason and audit.
        """
        cycle = self.db.execute(
            select(ReviewCycle).where(ReviewCycle.cycle_id == cycle_id)
        ).scalar_one_or_none()
        if not cycle:
            return

        if cycle.stage in ("CLOSED", "ARCHIVED"):
            if not is_administrative_correction or not correction_reason:
                raise ClosedCycleModificationException(
                    f"Review cycle {cycle_id} is {cycle.stage}. Unauthorized modifications are rejected. "
                    "Administrative corrections require authorized role, explicit justification, and audit trail."
                )
            
            # Record explicit administrative correction event
            import uuid
            audit = AuditEvent(
                event_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                actor_id=actor_id,
                entity_name="REVIEW_CYCLE",
                entity_id=cycle_id,
                operation_type="CORRECTION",
                review_cycle_id=cycle_id,
                reason=correction_reason
            )
            self.db.add(audit)
            self.db.commit()
