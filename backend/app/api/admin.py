from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.permissions.rbac import get_current_user, require_roles, AuthenticatedUser
from backend.generator.config import get_generator_config
from backend.generator.runner import generate_all_data, insert_into_database
from backend.validators.engine import ValidationEngine

router = APIRouter(prefix="/admin", tags=["Administration & Operations"])


class GenerateDataRequest(BaseModel):
    mode: str = "starter"
    seed: int = 20261022
    load_into_db: bool = True


@router.post("/generate-data")
def trigger_data_generation(
    payload: GenerateDataRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles(["ADMIN", "IT_OPS"]))
) -> Dict[str, Any]:
    """
    Executes the deterministic synthetic data generator.
    """
    if payload.mode not in ("starter", "full"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mode must be 'starter' or 'full'")

    config = get_generator_config(mode=payload.mode, seed=payload.seed)
    tables_data, ground_truth = generate_all_data(config)

    if payload.load_into_db:
        insert_into_database(tables_data)

    return {
        "status": "SUCCESS",
        "mode": payload.mode,
        "seed": payload.seed,
        "row_counts": {k: len(v) for k, v in tables_data.items()},
        "ground_truth_records": len(ground_truth)
    }


@router.post("/validate-data")
def trigger_data_validation(
    dataset_dir: Optional[str] = "generated_data/starter",
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_roles(["ADMIN", "IT_OPS", "HR_PARTNER"]))
) -> Dict[str, Any]:
    """
    Executes the 15-point automated validation engine.
    """
    from backend.validators.runner import load_dataset_from_json_dir
    try:
        tables_data, ground_truth = load_dataset_from_json_dir(dataset_dir)
        engine = ValidationEngine()
        report = engine.validate_dataset(tables_data, ground_truth)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
