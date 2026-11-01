from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.app.core.database import get_db
from backend.app.models.employee import Employee, EmployeeManagerHistory
from backend.app.models.goal import Goal, KeyResult
from backend.app.models.check_in import CheckIn, Evidence
from backend.app.models.feedback import Feedback
from backend.app.models.competency import Competency
from backend.app.models.review import Review
from backend.app.models.development_plan import DevelopmentPlan
from backend.app.schemas.schemas import EmployeeResponse, EmployeeCreate, ManagerTransferRequest
from backend.app.permissions.rbac import get_current_user, require_roles, AuthenticatedUser
from backend.app.services.org_service import OrganizationService, CircularHierarchyException

router = APIRouter(tags=["Employees & Organization"])


@router.get("/employees", response_model=List[EmployeeResponse])
def list_employees(
    department: Optional[str] = None,
    manager_id: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(Employee)
    if department:
        query = query.where(Employee.department == department)
    if manager_id:
        query = query.where(Employee.manager_id == manager_id)
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Employee.first_name.ilike(search_filter)) |
            (Employee.last_name.ilike(search_filter)) |
            (Employee.email.ilike(search_filter)) |
            (Employee.employee_id.ilike(search_filter))
        )
    query = query.offset(skip).limit(limit)
    employees = db.execute(query).scalars().all()
    return employees


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    emp = db.execute(select(Employee).where(Employee.employee_id == employee_id)).scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")
    return emp


@router.get("/employees/{employee_id}/performance-profile")
def get_employee_performance_profile(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns complete 360-degree performance profile for an employee:
    Basic profile, reporting manager, direct report count, active goals with Key Results,
    check-in history with attached evidence, 360 feedback, review history, and development plans.
    """
    emp = db.execute(select(Employee).where(Employee.employee_id == employee_id)).scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")

    # Manager details
    manager_info = None
    if emp.manager_id:
        mgr = db.execute(select(Employee).where(Employee.employee_id == emp.manager_id)).scalar_one_or_none()
        if mgr:
            manager_info = {
                "employee_id": mgr.employee_id,
                "full_name": mgr.full_name,
                "job_title": mgr.job_title,
                "department": mgr.department,
                "email": mgr.email
            }

    # Direct reports count
    direct_reports_count = db.execute(
        select(func.count(Employee.employee_id)).where(Employee.manager_id == employee_id)
    ).scalar() or 0

    # Goals with Key Results
    goals = db.execute(
        select(Goal).where(Goal.employee_id == employee_id).order_by(Goal.due_date.desc())
    ).scalars().all()

    goal_list = []
    for g in goals:
        krs = db.execute(select(KeyResult).where(KeyResult.goal_id == g.goal_id)).scalars().all()
        goal_list.append({
            "goal_id": g.goal_id,
            "title": g.title,
            "description": g.description,
            "category": g.category,
            "priority": g.priority,
            "status": g.status,
            "weight": float(g.weight),
            "calculated_progress": float(g.calculated_progress),
            "start_date": str(g.start_date),
            "due_date": str(g.due_date),
            "review_cycle_id": g.review_cycle_id,
            "key_results": [
                {
                    "key_result_id": kr.key_result_id,
                    "metric_name": kr.metric_name,
                    "metric_direction": kr.metric_direction,
                    "baseline_value": float(kr.baseline_value),
                    "target_value": float(kr.target_value),
                    "current_value": float(kr.current_value),
                    "unit": kr.unit,
                    "weight": float(kr.weight),
                    "progress_percentage": float(kr.progress_percentage),
                    "status": kr.status
                }
                for kr in krs
            ]
        })

    # Check-ins with Evidence
    check_ins = db.execute(
        select(CheckIn).where(CheckIn.employee_id == employee_id).order_by(CheckIn.check_in_date.desc())
    ).scalars().all()

    check_in_list = []
    for c in check_ins:
        evs = db.execute(select(Evidence).where(Evidence.check_in_id == c.check_in_id)).scalars().all()
        check_in_list.append({
            "check_in_id": c.check_in_id,
            "goal_id": c.goal_id,
            "review_cycle_id": c.review_cycle_id,
            "check_in_date": str(c.check_in_date),
            "progress_update": float(c.progress_update),
            "employee_comments": c.employee_comments,
            "manager_comments": c.manager_comments,
            "blockers": c.blockers,
            "next_steps": c.next_steps,
            "evidences": [
                {
                    "evidence_id": ev.evidence_id,
                    "evidence_type": ev.evidence_type,
                    "reference_url": ev.reference_url,
                    "description": ev.description,
                    "uploaded_by": ev.uploaded_by,
                    "verification_status": ev.verification_status
                }
                for ev in evs
            ]
        })

    # 360 Feedback received
    feedbacks = db.execute(
        select(Feedback).where(Feedback.subject_employee_id == employee_id).order_by(Feedback.submission_date.desc())
    ).scalars().all()

    feedback_list = []
    for fb in feedbacks:
        comp = db.execute(select(Competency).where(Competency.competency_id == fb.competency_id)).scalar_one_or_none()
        feedback_list.append({
            "feedback_id": fb.feedback_id,
            "reviewer_employee_id": fb.reviewer_employee_id,
            "review_cycle_id": fb.review_cycle_id,
            "feedback_type": fb.feedback_type,
            "competency_id": fb.competency_id,
            "competency_name": comp.name if comp else fb.competency_id,
            "competency_category": comp.category if comp else "General",
            "rating": float(fb.rating),
            "comments": fb.comments,
            "status": fb.status,
            "submitted_at": str(fb.submission_date)
        })

    # Performance Reviews
    reviews = db.execute(
        select(Review).where(Review.employee_id == employee_id).order_by(Review.created_at.desc())
    ).scalars().all()

    review_list = [
        {
            "review_id": r.review_id,
            "review_cycle_id": r.review_cycle_id,
            "stage": r.stage,
            "goal_score": float(r.goal_score) if r.goal_score is not None else None,
            "competency_score": float(r.competency_score) if r.competency_score is not None else None,
            "feedback_score": float(r.feedback_score) if r.feedback_score is not None else None,
            "final_score": float(r.final_score) if r.final_score is not None else None,
            "rating_category": r.rating_category,
            "manager_comments": r.manager_comments,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in reviews
    ]

    # Development Plans (IDPs)
    dev_plans = db.execute(
        select(DevelopmentPlan).where(DevelopmentPlan.employee_id == employee_id).order_by(DevelopmentPlan.created_at.desc())
    ).scalars().all()

    dev_plan_list = []
    for dp in dev_plans:
        comp = db.execute(select(Competency).where(Competency.competency_id == dp.competency_id)).scalar_one_or_none()
        dev_plan_list.append({
            "plan_id": dp.plan_id,
            "competency_id": dp.competency_id,
            "competency_name": comp.name if comp else dp.competency_id,
            "current_level": dp.current_level,
            "target_level": dp.target_level,
            "recommended_action": dp.recommended_action,
            "learning_resources": dp.learning_resources,
            "start_date": str(dp.start_date),
            "target_completion_date": str(dp.target_completion_date),
            "status": dp.status,
            "approval_status": dp.approval_status
        })

    # Historical Manager Assignments
    mgr_hist = db.execute(
        select(EmployeeManagerHistory).where(EmployeeManagerHistory.employee_id == employee_id).order_by(EmployeeManagerHistory.effective_start_date.desc())
    ).scalars().all()

    mgr_hist_list = [
        {
            "history_id": mh.history_id,
            "manager_id": mh.manager_id,
            "start_date": str(mh.effective_start_date),
            "end_date": str(mh.effective_end_date) if mh.effective_end_date else None,
            "is_current": mh.effective_end_date is None,
            "transfer_reason": mh.transfer_reason
        }
        for mh in mgr_hist
    ]

    return {
        "employee": {
            "employee_id": emp.employee_id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "full_name": emp.full_name,
            "email": emp.email,
            "department": emp.department,
            "job_title": emp.job_title,
            "job_level": emp.job_level,
            "manager_id": emp.manager_id,
            "hire_date": str(emp.hire_date),
            "is_active": emp.is_active
        },
        "manager": manager_info,
        "direct_reports_count": direct_reports_count,
        "goals": goal_list,
        "check_ins": check_in_list,
        "feedbacks": feedback_list,
        "reviews": review_list,
        "development_plans": dev_plan_list,
        "manager_history": mgr_hist_list
    }


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles(["ADMIN", "HR_PARTNER"]))
):
    existing = db.execute(
        select(Employee).where(
            (Employee.employee_id == payload.employee_id) | (Employee.email == payload.email)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee ID or email already registered")

    org_service = OrganizationService(db)
    if payload.manager_id and org_service.check_circular_hierarchy(payload.employee_id, payload.manager_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Circular hierarchy detected")

    emp = Employee(
        employee_id=payload.employee_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        department=payload.department,
        job_title=payload.job_title,
        job_level=payload.job_level,
        manager_id=payload.manager_id,
        hire_date=payload.hire_date
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.get("/organization/hierarchy")
def get_organization_hierarchy(
    root_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    org_service = OrganizationService(db)
    return org_service.get_hierarchy_tree(root_id=root_id)


@router.post("/organization/transfer/{employee_id}", response_model=EmployeeResponse)
def transfer_manager(
    employee_id: str,
    payload: ManagerTransferRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles(["ADMIN", "HR_PARTNER"]))
):
    org_service = OrganizationService(db)
    try:
        emp = org_service.assign_manager(
            employee_id=employee_id,
            new_manager_id=payload.new_manager_id,
            effective_date=payload.effective_date,
            reason=payload.reason,
            actor_id=current_user.employee_id
        )
        return emp
    except CircularHierarchyException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
