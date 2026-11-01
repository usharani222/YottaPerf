from typing import List, Dict, Any, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from backend.app.core.database import get_db
from backend.app.models.employee import Employee, Manager
from backend.app.models.review_cycle import ReviewCycle
from backend.app.models.goal import Goal, KeyResult
from backend.app.models.check_in import CheckIn, Evidence
from backend.app.models.review import Review
from backend.app.models.competency import Competency
from backend.app.models.feedback import Feedback
from backend.app.models.development_plan import DevelopmentPlan
from backend.app.models.anomaly import Anomaly
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

# Pinned reference date for realistic enterprise time calculations
REF_DATE = date(2026, 6, 30)
CHECKIN_OVERDUE_DATE = date(2026, 6, 1)


@router.get("/dashboard")
def get_dashboard_summary(
    department: Optional[str] = None,
    review_cycle_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Computes live enterprise dashboard metrics and secondary operational health metrics
    from normalized PostgreSQL relational tables with optional department & cycle filters.
    """
    # 1. Total Employees
    emp_query = select(func.count(Employee.employee_id))
    if department and department != "ALL":
        emp_query = emp_query.where(Employee.department == department)
    total_employees = db.execute(emp_query).scalar() or 0

    # 2. Total Managers
    if department and department != "ALL":
        mgr_query = select(func.count(func.distinct(Manager.manager_id))).join(
            Employee, Employee.employee_id == Manager.employee_id
        ).where(Employee.department == department)
    else:
        mgr_query = select(func.count(Manager.manager_id))
    total_managers = db.execute(mgr_query).scalar() or 0

    # 3. Active Review Cycles
    cycle_query = select(func.count(ReviewCycle.cycle_id)).where(ReviewCycle.stage.in_(("OPEN", "EVALUATION")))
    if review_cycle_id and review_cycle_id != "ALL":
        cycle_query = cycle_query.where(ReviewCycle.cycle_id == review_cycle_id)
    active_cycles = db.execute(cycle_query).scalar() or 0

    # 4. Total Goals & Key Results
    goals_base = select(Goal)
    if department and department != "ALL":
        goals_base = goals_base.join(Employee, Employee.employee_id == Goal.employee_id).where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        goals_base = goals_base.where(Goal.review_cycle_id == review_cycle_id)

    total_goals_query = select(func.count(Goal.goal_id))
    avg_progress_query = select(func.avg(Goal.calculated_progress))
    if department and department != "ALL":
        total_goals_query = total_goals_query.join(Employee, Employee.employee_id == Goal.employee_id).where(Employee.department == department)
        avg_progress_query = avg_progress_query.join(Employee, Employee.employee_id == Goal.employee_id).where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        total_goals_query = total_goals_query.where(Goal.review_cycle_id == review_cycle_id)
        avg_progress_query = avg_progress_query.where(Goal.review_cycle_id == review_cycle_id)

    total_goals = db.execute(total_goals_query).scalar() or 0
    avg_goal_progress = db.execute(avg_progress_query).scalar() or 0.0

    # Key Results
    kr_query = select(func.count(KeyResult.key_result_id)).join(Goal, Goal.goal_id == KeyResult.goal_id)
    if department and department != "ALL":
        kr_query = kr_query.join(Employee, Employee.employee_id == Goal.employee_id).where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        kr_query = kr_query.where(Goal.review_cycle_id == review_cycle_id)
    total_krs = db.execute(kr_query).scalar() or 0

    # 5. Review Stage Metrics (Mutually Exclusive)
    rev_base = select(Review)
    if department and department != "ALL":
        rev_base = rev_base.join(Employee, Employee.employee_id == Review.employee_id).where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        rev_base = rev_base.where(Review.review_cycle_id == review_cycle_id)

    total_rev_q = select(func.count(Review.review_id))
    completed_rev_q = select(func.count(Review.review_id)).where(Review.stage == "COMPLETED")
    approved_rev_q = select(func.count(Review.review_id)).where(Review.stage == "APPROVED")
    pending_rev_q = select(func.count(Review.review_id)).where(Review.stage.notin_(("COMPLETED", "APPROVED")))

    if department and department != "ALL":
        total_rev_q = total_rev_q.join(Employee, Employee.employee_id == Review.employee_id).where(Employee.department == department)
        completed_rev_q = completed_rev_q.join(Employee, Employee.employee_id == Review.employee_id).where(Employee.department == department)
        approved_rev_q = approved_rev_q.join(Employee, Employee.employee_id == Review.employee_id).where(Employee.department == department)
        pending_rev_q = pending_rev_q.join(Employee, Employee.employee_id == Review.employee_id).where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        total_rev_q = total_rev_q.where(Review.review_cycle_id == review_cycle_id)
        completed_rev_q = completed_rev_q.where(Review.review_cycle_id == review_cycle_id)
        approved_rev_q = approved_rev_q.where(Review.review_cycle_id == review_cycle_id)
        pending_rev_q = pending_rev_q.where(Review.review_cycle_id == review_cycle_id)

    total_reviews = db.execute(total_rev_q).scalar() or 0
    completed_reviews = db.execute(completed_rev_q).scalar() or 0
    approved_reviews = db.execute(approved_rev_q).scalar() or 0
    pending_reviews = db.execute(pending_rev_q).scalar() or 0

    finalized_reviews = completed_reviews + approved_reviews
    review_completion_pct = round((finalized_reviews / total_reviews * 100.0), 1) if total_reviews > 0 else 0.0

    # 6. Secondary Operational Health Metrics
    # Goals at Risk: progress < 40% or status AT_RISK and not completed
    risk_q = select(func.count(Goal.goal_id)).where(
        and_(
            Goal.status != "COMPLETED",
            or_(Goal.status == "AT_RISK", Goal.calculated_progress < 40.0)
        )
    )
    # Overdue Goals: due_date < REF_DATE and not completed
    overdue_g_q = select(func.count(Goal.goal_id)).where(
        and_(Goal.status != "COMPLETED", Goal.due_date < REF_DATE)
    )
    # Overdue Check-ins: Active goals without check-in on or after CHECKIN_OVERDUE_DATE
    overdue_chk_q = select(func.count(Goal.goal_id)).where(
        and_(
            Goal.status == "ACTIVE",
            ~Goal.goal_id.in_(
                select(CheckIn.goal_id).where(CheckIn.check_in_date >= CHECKIN_OVERDUE_DATE)
            )
        )
    )

    if department and department != "ALL":
        risk_q = risk_q.join(Employee, Employee.employee_id == Goal.employee_id).where(Employee.department == department)
        overdue_g_q = overdue_g_q.join(Employee, Employee.employee_id == Goal.employee_id).where(Employee.department == department)
        overdue_chk_q = overdue_chk_q.join(Employee, Employee.employee_id == Goal.employee_id).where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        risk_q = risk_q.where(Goal.review_cycle_id == review_cycle_id)
        overdue_g_q = overdue_g_q.where(Goal.review_cycle_id == review_cycle_id)
        overdue_chk_q = overdue_chk_q.where(Goal.review_cycle_id == review_cycle_id)

    goals_at_risk = db.execute(risk_q).scalar() or 0
    overdue_goals = db.execute(overdue_g_q).scalar() or 0
    overdue_checkins = db.execute(overdue_chk_q).scalar() or 0

    # 7. Development Plans & Overdue IDPs
    dev_query = select(func.count(DevelopmentPlan.plan_id)).where(DevelopmentPlan.status == "IN_PROGRESS")
    overdue_dev_q = select(func.count(DevelopmentPlan.plan_id)).where(
        and_(DevelopmentPlan.status != "COMPLETED", DevelopmentPlan.target_completion_date < REF_DATE)
    )
    if department and department != "ALL":
        dev_query = dev_query.join(Employee, Employee.employee_id == DevelopmentPlan.employee_id).where(Employee.department == department)
        overdue_dev_q = overdue_dev_q.join(Employee, Employee.employee_id == DevelopmentPlan.employee_id).where(Employee.department == department)

    active_dev_plans = db.execute(dev_query).scalar() or 0
    overdue_dev_plans = db.execute(overdue_dev_q).scalar() or 0

    # 8. Anomalies
    open_anomalies = db.execute(
        select(func.count(Anomaly.anomaly_id)).where(Anomaly.detection_status != "RESOLVED")
    ).scalar() or 0

    critical_anomalies = db.execute(
        select(func.count(Anomaly.anomaly_id)).where(
            and_(Anomaly.severity == "CRITICAL", Anomaly.detection_status != "RESOLVED")
        )
    ).scalar() or 0

    return {
        # Core Primary Metrics
        "total_employees": total_employees,
        "total_managers": total_managers,
        "active_review_cycles": active_cycles,
        "total_goals": total_goals,
        "total_key_results": total_krs,
        "average_goal_progress": round(float(avg_goal_progress), 2),
        "completed_reviews": completed_reviews,
        "approved_reviews": approved_reviews,
        "pending_reviews": pending_reviews,
        "total_reviews": total_reviews,
        "review_completion_percentage": review_completion_pct,
        "development_plans_in_progress": active_dev_plans,
        "open_anomalies": open_anomalies,

        # Derived Operational Health Metrics
        "goals_at_risk": goals_at_risk,
        "overdue_goals": overdue_goals,
        "overdue_checkins": overdue_checkins,
        "critical_anomalies": critical_anomalies,
        "overdue_dev_plans": overdue_dev_plans,
        "filters_applied": {
            "department": department or "ALL",
            "review_cycle_id": review_cycle_id or "ALL"
        }
    }


@router.get("/goals")
def get_goal_analytics(
    department: Optional[str] = None,
    review_cycle_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Computes average goal progress and goal count grouped by department.
    """
    query = (
        select(
            Employee.department,
            func.count(Goal.goal_id).label("goal_count"),
            func.avg(Goal.calculated_progress).label("avg_progress")
        )
        .join(Goal, Goal.employee_id == Employee.employee_id)
    )

    if department and department != "ALL":
        query = query.where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        query = query.where(Goal.review_cycle_id == review_cycle_id)

    results = db.execute(
        query.group_by(Employee.department)
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
    department: Optional[str] = None,
    review_cycle_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Aggregates performance rating distributions and mutually exclusive review stage breakdowns.
    """
    dist_q = select(Review.rating_category, func.count(Review.review_id))
    stage_q = select(Review.stage, func.count(Review.review_id))

    if department and department != "ALL":
        dist_q = dist_q.join(Employee, Employee.employee_id == Review.employee_id).where(Employee.department == department)
        stage_q = stage_q.join(Employee, Employee.employee_id == Review.employee_id).where(Employee.department == department)
    if review_cycle_id and review_cycle_id != "ALL":
        dist_q = dist_q.where(Review.review_cycle_id == review_cycle_id)
        stage_q = stage_q.where(Review.review_cycle_id == review_cycle_id)

    dist_results = db.execute(dist_q.group_by(Review.rating_category)).all()
    stage_results = db.execute(stage_q.group_by(Review.stage)).all()

    stage_counts = {r[0]: r[1] for r in stage_results}

    # Complete mutually exclusive lifecycle specification
    all_stages = [
        "DRAFT",
        "SELF_REVIEW_PENDING",
        "MANAGER_REVIEW_PENDING",
        "HR_REVIEW_PENDING",
        "APPROVED",
        "COMPLETED",
        "REJECTED",
        "RETURNED_FOR_REVISION"
    ]

    mutually_exclusive_stages = [
        {"stage": s, "count": stage_counts.get(s, 0)}
        for s in all_stages
        if stage_counts.get(s, 0) > 0 or s in ("COMPLETED", "APPROVED", "MANAGER_REVIEW_PENDING", "SELF_REVIEW_PENDING")
    ]

    total_reviews = sum(r[1] for r in stage_results)

    return {
        "rating_distribution": [{"category": r[0], "count": r[1]} for r in dist_results],
        "stage_distribution": mutually_exclusive_stages,
        "total_reviews": total_reviews
    }


@router.get("/competencies")
def get_competency_analytics(
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Computes average feedback rating per competency category.
    """
    query = (
        select(
            Competency.category,
            func.avg(Feedback.rating).label("avg_rating"),
            func.count(Feedback.feedback_id).label("feedback_count")
        )
        .join(Feedback, Feedback.competency_id == Competency.competency_id)
    )

    if department and department != "ALL":
        query = query.join(Employee, Employee.employee_id == Feedback.subject_employee_id).where(Employee.department == department)

    results = db.execute(
        query.group_by(Competency.category)
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
