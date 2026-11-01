from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.app.core.database import get_db
from backend.app.models.employee import Employee, Manager
from backend.app.models.review_cycle import ReviewCycle
from backend.app.models.goal import Goal
from backend.app.models.check_in import CheckIn
from backend.app.models.review import Review
from backend.app.models.competency import Competency
from backend.app.models.feedback import Feedback
from backend.app.models.development_plan import DevelopmentPlan
from backend.app.models.anomaly import Anomaly
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])


@router.get("/dashboard")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Computes live enterprise dashboard metrics from relational tables.
    """
    total_employees = db.execute(select(func.count(Employee.employee_id))).scalar() or 0
    total_managers = db.execute(select(func.count(Manager.manager_id))).scalar() or 0
    active_cycles = db.execute(
        select(func.count(ReviewCycle.cycle_id)).where(ReviewCycle.stage.in_(("OPEN", "EVALUATION")))
    ).scalar() or 0
    total_goals = db.execute(select(func.count(Goal.goal_id))).scalar() or 0
    avg_goal_progress = db.execute(select(func.avg(Goal.calculated_progress))).scalar() or 0.0

    completed_reviews = db.execute(
        select(func.count(Review.review_id)).where(Review.stage.in_(("APPROVED", "COMPLETED")))
    ).scalar() or 0
    pending_reviews = db.execute(
        select(func.count(Review.review_id)).where(Review.stage.notin_(("APPROVED", "COMPLETED")))
    ).scalar() or 0

    active_dev_plans = db.execute(
        select(func.count(DevelopmentPlan.plan_id)).where(DevelopmentPlan.status == "IN_PROGRESS")
    ).scalar() or 0

    open_anomalies = db.execute(
        select(func.count(Anomaly.anomaly_id)).where(Anomaly.detection_status != "RESOLVED")
    ).scalar() or 0

    return {
        "total_employees": total_employees,
        "total_managers": total_managers,
        "active_review_cycles": active_cycles,
        "total_goals": total_goals,
        "average_goal_progress": round(float(avg_goal_progress), 2),
        "completed_reviews": completed_reviews,
        "pending_reviews": pending_reviews,
        "development_plans_in_progress": active_dev_plans,
        "open_anomalies": open_anomalies,
    }


@router.get("/goals")
def get_goal_analytics(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Computes average goal progress and goal count grouped by department.
    """
    results = db.execute(
        select(
            Employee.department,
            func.count(Goal.goal_id).label("goal_count"),
            func.avg(Goal.calculated_progress).label("avg_progress")
        )
        .join(Goal, Goal.employee_id == Employee.employee_id)
        .group_by(Employee.department)
        .order_by(func.avg(Goal.calculated_progress).desc())
    ).all()

    return [
        {
            "department": r.department,
            "goal_count": r.goal_count,
            "avg_progress": round(float(r.avg_progress or 0.0), 2)
        }
        for r in results
    ]


@router.get("/reviews")
def get_review_analytics(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Aggregates performance rating distributions and stage completion rates.
    """
    dist_results = db.execute(
        select(Review.rating_category, func.count(Review.review_id))
        .group_by(Review.rating_category)
    ).all()

    stage_results = db.execute(
        select(Review.stage, func.count(Review.review_id))
        .group_by(Review.stage)
    ).all()

    return {
        "rating_distribution": [{"category": r[0], "count": r[1]} for r in dist_results],
        "stage_distribution": [{"stage": r[0], "count": r[1]} for r in stage_results]
    }


@router.get("/competencies")
def get_competency_analytics(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Computes average feedback rating per competency category.
    """
    results = db.execute(
        select(
            Competency.category,
            func.avg(Feedback.rating).label("avg_rating"),
            func.count(Feedback.feedback_id).label("feedback_count")
        )
        .join(Feedback, Feedback.competency_id == Competency.competency_id)
        .group_by(Competency.category)
        .order_by(func.avg(Feedback.rating).desc())
    ).all()

    return [
        {
            "category": r.category,
            "avg_rating": round(float(r.avg_rating or 0.0), 2),
            "feedback_count": r.feedback_count
        }
        for r in results
    ]


@router.get("/anomalies")
def get_anomaly_analytics(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Aggregates anomalies by issue type and severity.
    """
    type_results = db.execute(
        select(Anomaly.issue_type, func.count(Anomaly.anomaly_id))
        .group_by(Anomaly.issue_type)
    ).all()

    sev_results = db.execute(
        select(Anomaly.severity, func.count(Anomaly.anomaly_id))
        .group_by(Anomaly.severity)
    ).all()

    return {
        "by_type": [{"issue_type": r[0], "count": r[1]} for r in type_results],
        "by_severity": [{"severity": r[0], "count": r[1]} for r in sev_results]
    }
