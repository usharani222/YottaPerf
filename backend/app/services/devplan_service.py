from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.development_plan import (
    DevelopmentPlan, DevelopmentActivity, DevelopmentPlanApproval
)
from backend.app.models.competency import Competency


class DevelopmentPlanService:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(
        self,
        plan_id: str,
        employee_id: str,
        competency_id: str,
        current_level: str,
        target_level: str,
        recommended_action: str,
        start_date: date,
        target_completion_date: date,
        review_id: Optional[str] = None,
        learning_resources: Optional[str] = None
    ) -> DevelopmentPlan:
        if target_completion_date < start_date:
            raise ValueError("target_completion_date cannot be earlier than start_date")

        plan = DevelopmentPlan(
            plan_id=plan_id,
            employee_id=employee_id,
            review_id=review_id,
            competency_id=competency_id,
            current_level=current_level,
            target_level=target_level,
            recommended_action=recommended_action,
            learning_resources=learning_resources,
            start_date=start_date,
            target_completion_date=target_completion_date,
            status="IN_PROGRESS",
            approval_status="PENDING"
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def approve_plan(
        self,
        plan_id: str,
        approver_id: str,
        approval_role: str = "MANAGER",
        decision: str = "APPROVED",
        comments: Optional[str] = None
    ) -> DevelopmentPlanApproval:
        plan = self.db.execute(
            select(DevelopmentPlan).where(DevelopmentPlan.plan_id == plan_id)
        ).scalar_one_or_none()
        if not plan:
            raise ValueError(f"Development plan {plan_id} not found")

        import uuid
        appr = DevelopmentPlanApproval(
            approval_id=f"DPA-{uuid.uuid4().hex[:8].upper()}",
            plan_id=plan_id,
            approver_id=approver_id,
            approval_role=approval_role,
            decision=decision,
            comments=comments
        )
        self.db.add(appr)

        plan.approval_status = decision
        plan.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(appr)
        return appr
