from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.check_in import CheckIn, Evidence
from backend.app.models.goal import Goal
from backend.app.services.cycle_service import ReviewCycleService


class CheckInService:
    def __init__(self, db: Session):
        self.db = db
        self.cycle_service = ReviewCycleService(db)

    def create_check_in(
        self,
        check_in_id: str,
        employee_id: str,
        goal_id: str,
        review_cycle_id: str,
        check_in_date: date,
        progress_update: float,
        employee_comments: str,
        manager_comments: Optional[str] = None,
        blockers: Optional[str] = None,
        next_steps: Optional[str] = None,
        evidence_reference_url: Optional[str] = None,
        evidence_type: str = "CODE_PR",
        evidence_description: Optional[str] = None
    ) -> CheckIn:
        self.cycle_service.validate_cycle_modification_allowed(review_cycle_id, actor_id=employee_id)

        goal = self.db.execute(select(Goal).where(Goal.goal_id == goal_id)).scalar_one_or_none()
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        check_in = CheckIn(
            check_in_id=check_in_id,
            employee_id=employee_id,
            goal_id=goal_id,
            review_cycle_id=review_cycle_id,
            check_in_date=check_in_date,
            progress_update=progress_update,
            employee_comments=employee_comments,
            manager_comments=manager_comments,
            blockers=blockers,
            next_steps=next_steps
        )
        self.db.add(check_in)
        self.db.flush()

        # Link evidence if provided
        if evidence_reference_url:
            import uuid
            evd_id = f"EVD-{uuid.uuid4().hex[:8].upper()}"
            evd = Evidence(
                evidence_id=evd_id,
                check_in_id=check_in_id,
                evidence_type=evidence_type,
                reference_url=evidence_reference_url,
                description=evidence_description or f"Supporting evidence for check-in {check_in_id}",
                uploaded_by=employee_id,
                uploaded_date=check_in_date,
                verification_status="VERIFIED"
            )
            self.db.add(evd)

        self.db.commit()
        self.db.refresh(check_in)
        return check_in
