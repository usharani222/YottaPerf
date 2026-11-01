from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.employee import Employee, EmployeeManagerHistory, Manager
from backend.app.models.audit import AuditEvent


class CircularHierarchyException(Exception):
    pass


class OrganizationService:
    def __init__(self, db: Session):
        self.db = db

    def check_circular_hierarchy(self, employee_id: str, proposed_manager_id: Optional[str]) -> bool:
        """
        Detects if assigning proposed_manager_id to employee_id creates a cycle.
        Traverses ancestors starting from proposed_manager_id up to root.
        Returns True if a circular reporting chain is detected.
        """
        if not proposed_manager_id:
            return False
        if employee_id == proposed_manager_id:
            return True

        visited: Set[str] = {employee_id}
        current_id: Optional[str] = proposed_manager_id

        while current_id:
            if current_id in visited:
                return True
            visited.add(current_id)

            mgr = self.db.execute(
                select(Employee.manager_id).where(Employee.employee_id == current_id)
            ).scalar_one_or_none()

            current_id = mgr

        return False

    def assign_manager(
        self,
        employee_id: str,
        new_manager_id: Optional[str],
        effective_date: Optional[date] = None,
        reason: Optional[str] = None,
        actor_id: Optional[str] = None
    ) -> Employee:
        """
        Assigns or transfers an employee to a new manager, maintaining historical records
        and preventing circular hierarchy.
        """
        if effective_date is None:
            effective_date = date.today()

        emp = self.db.execute(
            select(Employee).where(Employee.employee_id == employee_id)
        ).scalar_one_or_none()
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")

        if new_manager_id:
            mgr = self.db.execute(
                select(Employee).where(Employee.employee_id == new_manager_id)
            ).scalar_one_or_none()
            if not mgr:
                raise ValueError(f"Manager {new_manager_id} not found")

            # Circular hierarchy prevention
            if self.check_circular_hierarchy(employee_id, new_manager_id):
                raise CircularHierarchyException(
                    f"Circular hierarchy detected: assigning {new_manager_id} as manager to {employee_id} creates a reporting loop"
                )

        old_manager_id = emp.manager_id

        # Close existing active history record if exists
        active_hist = self.db.execute(
            select(EmployeeManagerHistory).where(
                EmployeeManagerHistory.employee_id == employee_id,
                EmployeeManagerHistory.effective_end_date.is_(None)
            )
        ).scalar_one_or_none()

        if active_hist:
            active_hist.effective_end_date = effective_date

        # Insert new history if a new manager is assigned
        if new_manager_id:
            import uuid
            hist_id = f"EMH-{uuid.uuid4().hex[:8].upper()}"
            new_hist = EmployeeManagerHistory(
                history_id=hist_id,
                employee_id=employee_id,
                manager_id=new_manager_id,
                effective_start_date=effective_date,
                effective_end_date=None,
                transfer_reason=reason or "Manager transfer"
            )
            self.db.add(new_hist)

        # Update current employee record
        emp.manager_id = new_manager_id
        emp.updated_at = datetime.now(timezone.utc)

        # Record audit event
        import uuid
        audit = AuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            actor_id=actor_id or employee_id,
            entity_name="EMPLOYEE_MANAGER_TRANSFER",
            entity_id=employee_id,
            operation_type="TRANSITION",
            old_values={"manager_id": old_manager_id},
            new_values={"manager_id": new_manager_id},
            reason=reason or "Manager assignment/transfer"
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def get_hierarchy_tree(self, root_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Builds a hierarchical org chart tree.
        """
        employees = self.db.execute(select(Employee)).scalars().all()
        emp_dict = {
            e.employee_id: {
                "id": e.employee_id,
                "name": e.full_name,
                "title": e.job_title,
                "department": e.department,
                "level": e.job_level,
                "manager_id": e.manager_id,
                "children": []
            }
            for e in employees
        }

        roots = []
        for emp_id, node in emp_dict.items():
            mgr_id = node["manager_id"]
            if mgr_id and mgr_id in emp_dict:
                emp_dict[mgr_id]["children"].append(node)
            else:
                roots.append(node)

        if root_id and root_id in emp_dict:
            return [emp_dict[root_id]]
        return roots
