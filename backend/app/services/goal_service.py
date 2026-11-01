from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.goal import Goal, KeyResult, GoalHistory
from backend.app.models.review_cycle import ReviewCycle
from backend.app.models.audit import AuditEvent
from backend.app.services.cycle_service import ReviewCycleService


class InvalidProgressException(Exception):
    pass


def calculate_kr_progress(metric_direction: str, baseline: float, target: float, current: float) -> float:
    """
    Mathematical formula calculation for Key Results:
    Increasing: ((current - baseline) / (target - baseline)) * 100
    Decreasing: ((baseline - current) / (baseline - target)) * 100
    """
    if metric_direction == "INCREASING":
        denominator = target - baseline
        if abs(denominator) < 1e-9:
            return 100.0 if current >= target else 0.0
        progress = ((current - baseline) / denominator) * 100.0
    else:  # DECREASING
        denominator = baseline - target
        if abs(denominator) < 1e-9:
            return 100.0 if current <= target else 0.0
        progress = ((baseline - current) / denominator) * 100.0

    if progress < 0.0:
        return 0.0
    return round(progress, 2)


class GoalService:
    def __init__(self, db: Session):
        self.db = db
        self.cycle_service = ReviewCycleService(db)

    def create_goal(
        self,
        goal_id: str,
        employee_id: str,
        review_cycle_id: str,
        title: str,
        category: str,
        start_date: date,
        due_date: date,
        description: Optional[str] = None,
        priority: str = "MEDIUM",
        weight: float = 1.0,
        created_by: Optional[str] = None,
        is_admin_correction: bool = False,
        correction_reason: Optional[str] = None,
    ) -> Goal:
        # Check closed cycle modification constraint
        self.cycle_service.validate_cycle_modification_allowed(
            cycle_id=review_cycle_id,
            is_administrative_correction=is_admin_correction,
            correction_reason=correction_reason,
            actor_id=created_by or employee_id
        )

        if due_date < start_date:
            raise ValueError("Goal due_date cannot be earlier than start_date")
        if weight <= 0:
            raise ValueError("Goal weight must be positive")

        goal = Goal(
            goal_id=goal_id,
            employee_id=employee_id,
            review_cycle_id=review_cycle_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            start_date=start_date,
            due_date=due_date,
            weight=weight,
            calculated_progress=0.00,
            status="DRAFT",
            created_by=created_by or employee_id,
            approved_by=None
        )
        self.db.add(goal)

        # Snapshot version 1
        import uuid
        gh = GoalHistory(
            history_id=f"GH-{uuid.uuid4().hex[:8].upper()}",
            goal_id=goal_id,
            version_number=1,
            title=title,
            status="DRAFT",
            calculated_progress=0.00,
            changed_by=created_by or employee_id,
            change_reason="Goal initial creation"
        )
        self.db.add(gh)

        self.db.commit()
        self.db.refresh(goal)
        return goal

    def add_key_result(
        self,
        key_result_id: str,
        goal_id: str,
        metric_name: str,
        baseline_value: float,
        target_value: float,
        current_value: float,
        unit: str,
        metric_direction: str = "INCREASING",
        weight: float = 1.0,
        actor_id: Optional[str] = None
    ) -> KeyResult:
        goal = self.db.execute(select(Goal).where(Goal.goal_id == goal_id)).scalar_one_or_none()
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        self.cycle_service.validate_cycle_modification_allowed(goal.review_cycle_id, actor_id=actor_id)

        # Calculate progress strictly from values
        progress = calculate_kr_progress(metric_direction, baseline_value, target_value, current_value)
        if progress > 200.0:
            raise InvalidProgressException(f"Progress {progress}% exceeds valid ceiling scale (200.0%)")

        status = "ACHIEVED" if progress >= 100.0 else ("ON_TRACK" if progress >= 70.0 else ("AT_RISK" if progress >= 40.0 else "BEHIND"))

        kr = KeyResult(
            key_result_id=key_result_id,
            goal_id=goal_id,
            metric_name=metric_name,
            metric_direction=metric_direction,
            baseline_value=baseline_value,
            target_value=target_value,
            current_value=current_value,
            unit=unit,
            weight=weight,
            progress_percentage=progress,
            status=status
        )
        self.db.add(kr)
        self.db.flush()

        # Recalculate parent goal progress
        self._reconcile_goal_progress(goal, actor_id=actor_id, reason=f"Added Key Result {key_result_id}")
        self.db.commit()
        self.db.refresh(kr)
        return kr

    def update_key_result_value(
        self,
        key_result_id: str,
        current_value: float,
        actor_id: Optional[str] = None
    ) -> KeyResult:
        kr = self.db.execute(
            select(KeyResult).where(KeyResult.key_result_id == key_result_id)
        ).scalar_one_or_none()
        if not kr:
            raise ValueError(f"Key Result {key_result_id} not found")

        goal = self.db.execute(select(Goal).where(Goal.goal_id == kr.goal_id)).scalar_one_or_none()
        if goal:
            self.cycle_service.validate_cycle_modification_allowed(goal.review_cycle_id, actor_id=actor_id)

        kr.current_value = current_value
        progress = calculate_kr_progress(
            kr.metric_direction, float(kr.baseline_value), float(kr.target_value), float(current_value)
        )
        if progress > 200.0:
            raise InvalidProgressException(f"Progress {progress}% exceeds valid scale bounds")

        kr.progress_percentage = progress
        kr.status = "ACHIEVED" if progress >= 100.0 else ("ON_TRACK" if progress >= 70.0 else ("AT_RISK" if progress >= 40.0 else "BEHIND"))
        kr.updated_at = datetime.now(timezone.utc)

        if goal:
            self._reconcile_goal_progress(goal, actor_id=actor_id, reason=f"Updated Key Result {key_result_id}")

        self.db.commit()
        self.db.refresh(kr)
        return kr

    def _reconcile_goal_progress(self, goal: Goal, actor_id: Optional[str] = None, reason: Optional[str] = None):
        """
        Recomputes Goal.calculated_progress from weighted Key Results.
        Creates GoalHistory snapshot.
        """
        krs = self.db.execute(
            select(KeyResult).where(KeyResult.goal_id == goal.goal_id)
        ).scalars().all()

        total_weight = sum(float(k.weight) for k in krs)
        if total_weight > 0:
            weighted_progress = sum(float(k.progress_percentage) * float(k.weight) for k in krs)
            goal.calculated_progress = round(weighted_progress / total_weight, 2)
        else:
            goal.calculated_progress = 0.00

        if goal.calculated_progress >= 100.0:
            goal.status = "COMPLETED"
        elif goal.calculated_progress > 0.0 and goal.status == "DRAFT":
            goal.status = "ACTIVE"

        goal.updated_at = datetime.now(timezone.utc)

        # Get latest version number
        latest_version = self.db.execute(
            select(GoalHistory.version_number)
            .where(GoalHistory.goal_id == goal.goal_id)
            .order_by(GoalHistory.version_number.desc())
        ).scalar() or 0

        import uuid
        gh = GoalHistory(
            history_id=f"GH-{uuid.uuid4().hex[:8].upper()}",
            goal_id=goal.goal_id,
            version_number=latest_version + 1,
            title=goal.title,
            status=goal.status,
            calculated_progress=goal.calculated_progress,
            changed_by=actor_id or goal.employee_id,
            change_reason=reason or "Key Results Progress Reconciliation"
        )
        self.db.add(gh)
