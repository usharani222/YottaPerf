import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.services.org_service import OrganizationService, CircularHierarchyException
from backend.app.models.employee import Employee


def test_01_employee_creation(client: TestClient, admin_headers: dict):
    """TEST 1: Employee creation via API."""
    payload = {
        "employee_id": "EMP-000991",
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith991@yottaperf.internal",
        "department": "Engineering",
        "job_title": "Software Engineer",
        "job_level": "IC3",
        "manager_id": None,
        "hire_date": "2024-01-15"
    }
    response = client.post("/api/employees", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["employee_id"] == "EMP-000991"
    assert data["full_name"] == "Alice Smith"
    assert data["is_active"] is True


def test_02_manager_assignment(db_session: Session, client: TestClient, admin_headers: dict):
    """TEST 2: Manager assignment and historical tracking."""
    org_svc = OrganizationService(db_session)
    
    # Create Manager Bob
    mgr = Employee(
        employee_id="EMP-000992",
        first_name="Bob",
        last_name="Manager",
        email="bob.manager992@yottaperf.internal",
        department="Engineering",
        job_title="Engineering Lead",
        job_level="M2",
        hire_date=date(2022, 1, 10)
    )
    db_session.merge(mgr)
    db_session.commit()

    # Assign Bob as manager to Alice
    transfer_payload = {
        "new_manager_id": "EMP-000992",
        "effective_date": "2024-06-01",
        "reason": "Team reorganization"
    }
    response = client.post("/api/organization/transfer/EMP-000991", json=transfer_payload, headers=admin_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["manager_id"] == "EMP-000992"


def test_03_circular_hierarchy_rejection(db_session: Session, client: TestClient, admin_headers: dict):
    """TEST 3: Circular reporting hierarchy rejection."""
    org_svc = OrganizationService(db_session)
    
    # Alice (EMP-000991) reports to Bob (EMP-000992)
    # Attempting to assign Alice as manager to Bob must trigger CircularHierarchyException
    with pytest.raises(CircularHierarchyException):
        org_svc.assign_manager("EMP-000992", "EMP-000991")

    # API must return 400 Bad Request
    transfer_payload = {
        "new_manager_id": "EMP-000991",
        "effective_date": "2024-06-15",
        "reason": "Invalid circular assignment"
    }
    response = client.post("/api/organization/transfer/EMP-000992", json=transfer_payload, headers=admin_headers)
    assert response.status_code == 400
    assert "circular" in response.json()["detail"].lower()
