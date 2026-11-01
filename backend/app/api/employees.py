from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.employee import Employee
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
