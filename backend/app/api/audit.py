from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.models.audit import AuditEvent
from backend.app.schemas.schemas import AuditEventResponse
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/audit-events", tags=["Audit & History"])


@router.get("", response_model=List[AuditEventResponse])
def list_audit_events(
    entity_name: Optional[str] = None,
    entity_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    query = select(AuditEvent)
    if entity_name:
        query = query.where(AuditEvent.entity_name == entity_name)
    if entity_id:
        query = query.where(AuditEvent.entity_id == entity_id)
    if operation_type:
        query = query.where(AuditEvent.operation_type == operation_type)

    query = query.order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit)
    return db.execute(query).scalars().all()
