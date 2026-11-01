from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.anomaly import Anomaly
from backend.app.schemas.schemas import AnomalyResponse, AnomalyResolveRequest
from backend.app.permissions.rbac import get_current_user, require_roles, AuthenticatedUser
from backend.app.services.anomaly_service import AnomalyService

router = APIRouter(prefix="/anomalies", tags=["Anomaly Center"])


@router.get("", response_model=List[AnomalyResponse])
def list_anomalies(
    detection_status: Optional[str] = None,
    issue_type: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(Anomaly)
    if detection_status:
        query = query.where(Anomaly.detection_status == detection_status)
    if issue_type:
        query = query.where(Anomaly.issue_type == issue_type)
    if severity:
        query = query.where(Anomaly.severity == severity)

    query = query.order_by(Anomaly.detection_timestamp.desc()).offset(skip).limit(limit)
    records = db.execute(query).scalars().all()

    # Enforce ground-truth isolation: Only ADMIN roles can view true ground-truth labels
    is_admin = "ADMIN" in current_user.roles
    response = []
    for a in records:
        response.append({
            "anomaly_id": a.anomaly_id,
            "issue_type": a.issue_type,
            "affected_entity": a.affected_entity,
            "affected_record_id": a.affected_record_id,
            "severity": a.severity,
            "description": a.description,
            "detection_status": a.detection_status,
            "ground_truth_label": a.ground_truth_label if is_admin else "RESTRICTED_SECURITY_ROLE",
            "expected_resolution": a.expected_resolution,
            "detection_timestamp": a.detection_timestamp,
            "resolution_notes": a.resolution_notes
        })
    return response


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
def get_anomaly(
    anomaly_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    ano = db.execute(select(Anomaly).where(Anomaly.anomaly_id == anomaly_id)).scalar_one_or_none()
    if not ano:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Anomaly {anomaly_id} not found")

    is_admin = "ADMIN" in current_user.roles
    return {
        "anomaly_id": ano.anomaly_id,
        "issue_type": ano.issue_type,
        "affected_entity": ano.affected_entity,
        "affected_record_id": ano.affected_record_id,
        "severity": ano.severity,
        "description": ano.description,
        "detection_status": ano.detection_status,
        "ground_truth_label": ano.ground_truth_label if is_admin else "RESTRICTED_SECURITY_ROLE",
        "expected_resolution": ano.expected_resolution,
        "detection_timestamp": ano.detection_timestamp,
        "resolution_notes": ano.resolution_notes
    }


@router.post("/{anomaly_id}/resolve", response_model=AnomalyResponse)
def resolve_anomaly(
    anomaly_id: str,
    payload: AnomalyResolveRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles(["ADMIN", "IT_OPS", "HR_PARTNER"]))
):
    svc = AnomalyService(db)
    try:
        ano = svc.resolve_anomaly(
            anomaly_id=anomaly_id,
            resolver_id=current_user.employee_id,
            resolution_status=payload.resolution_status,
            resolution_notes=payload.resolution_notes
        )
        return ano
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
