from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.anomaly import Anomaly
from backend.app.models.audit import AuditEvent


class AnomalyService:
    def __init__(self, db: Session):
        self.db = db

    def resolve_anomaly(
        self,
        anomaly_id: str,
        resolver_id: str,
        resolution_status: str = "RESOLVED",
        resolution_notes: Optional[str] = None
    ) -> Anomaly:
        ano = self.db.execute(
            select(Anomaly).where(Anomaly.anomaly_id == anomaly_id)
        ).scalar_one_or_none()
        if not ano:
            raise ValueError(f"Anomaly {anomaly_id} not found")

        ano.detection_status = resolution_status
        ano.resolved_by = resolver_id
        ano.resolved_at = datetime.now(timezone.utc)
        ano.resolution_notes = resolution_notes

        import uuid
        audit = AuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            actor_id=resolver_id,
            entity_name="ANOMALY",
            entity_id=anomaly_id,
            operation_type="UPDATE",
            new_values={"detection_status": resolution_status, "notes": resolution_notes},
            reason="Anomaly investigation & resolution"
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(ano)
        return ano
