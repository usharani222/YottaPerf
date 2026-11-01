from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    employee_id: str
    username: str
    roles: List[str]


class UserProfile(BaseModel):
    user_id: str
    employee_id: str
    username: str
    email: str
    full_name: str
    department: str
    job_title: str
    roles: List[str]


# Employee Schemas
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    department: str
    job_title: str
    job_level: str
    manager_id: Optional[str] = None
    hire_date: date


class EmployeeCreate(EmployeeBase):
    employee_id: str


class EmployeeResponse(EmployeeBase):
    employee_id: str
    is_active: bool
    full_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManagerTransferRequest(BaseModel):
    new_manager_id: Optional[str] = None
    effective_date: Optional[date] = None
    reason: Optional[str] = None


# Review Cycle Schemas
class ReviewCycleCreate(BaseModel):
    cycle_id: str
    cycle_name: str
    start_date: date
    end_date: date
    submission_deadline: date
    goal_weight: float = 50.0
    competency_weight: float = 30.0
    feedback_weight: float = 20.0


class ReviewCycleResponse(ReviewCycleCreate):
    stage: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CycleStageUpdateRequest(BaseModel):
    stage: str
    reason: Optional[str] = None


# Goal & Key Result Schemas
class KeyResultCreate(BaseModel):
    key_result_id: str
    metric_name: str
    baseline_value: float
    target_value: float
    current_value: float
    unit: str
    metric_direction: str = "INCREASING"
    weight: float = 1.0


class KeyResultUpdate(BaseModel):
    current_value: float


class KeyResultResponse(BaseModel):
    key_result_id: str
    goal_id: str
    metric_name: str
    metric_direction: str
    baseline_value: float
    target_value: float
    current_value: float
    unit: str
    weight: float
    progress_percentage: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class GoalCreate(BaseModel):
    goal_id: str
    employee_id: str
    review_cycle_id: str
    title: str
    description: Optional[str] = None
    category: str
    priority: str = "MEDIUM"
    start_date: date
    due_date: date
    weight: float = 1.0
    is_admin_correction: bool = False
    correction_reason: Optional[str] = None


class GoalResponse(BaseModel):
    goal_id: str
    employee_id: str
    review_cycle_id: str
    title: str
    description: Optional[str]
    category: str
    priority: str
    start_date: date
    due_date: date
    weight: float
    calculated_progress: float
    status: str
    created_by: str
    approved_by: Optional[str]
    key_results: List[KeyResultResponse] = []

    model_config = ConfigDict(from_attributes=True)


class GoalHistoryResponse(BaseModel):
    history_id: str
    goal_id: str
    version_number: int
    title: str
    status: str
    calculated_progress: float
    changed_by: str
    change_reason: str
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Check-in Schemas
class CheckInCreate(BaseModel):
    check_in_id: str
    employee_id: str
    goal_id: str
    review_cycle_id: str
    check_in_date: date
    progress_update: float
    employee_comments: str
    manager_comments: Optional[str] = None
    blockers: Optional[str] = None
    next_steps: Optional[str] = None
    evidence_reference_url: Optional[str] = None
    evidence_type: str = "CODE_PR"
    evidence_description: Optional[str] = None


class EvidenceResponse(BaseModel):
    evidence_id: str
    evidence_type: str
    reference_url: str
    description: str
    verification_status: str

    model_config = ConfigDict(from_attributes=True)


class CheckInResponse(BaseModel):
    check_in_id: str
    employee_id: str
    goal_id: str
    review_cycle_id: str
    check_in_date: date
    progress_update: float
    employee_comments: str
    manager_comments: Optional[str]
    blockers: Optional[str]
    next_steps: Optional[str]
    created_at: datetime
    evidences: List[EvidenceResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Feedback Schemas
class FeedbackCreate(BaseModel):
    feedback_id: str
    subject_employee_id: str
    review_cycle_id: str
    feedback_type: str
    competency_id: str
    rating: float
    comments: str
    evidence_id: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    subject_employee_id: str
    reviewer_employee_id: str
    review_cycle_id: str
    feedback_type: str
    competency_id: str
    rating: float
    comments: str
    submission_date: date
    status: str

    model_config = ConfigDict(from_attributes=True)


# Review Schemas
class ReviewCreate(BaseModel):
    review_id: str
    employee_id: str
    review_cycle_id: str


class ReviewResponse(BaseModel):
    review_id: str
    employee_id: str
    review_cycle_id: str
    goal_score: float
    competency_score: float
    feedback_score: float
    final_score: float
    rating_category: str
    stage: str
    self_comments: Optional[str]
    manager_comments: Optional[str]
    hr_comments: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ReviewTransitionRequest(BaseModel):
    target_stage: str
    comments: Optional[str] = None


# Development Plan Schemas
class DevelopmentPlanCreate(BaseModel):
    plan_id: str
    employee_id: str
    competency_id: str
    current_level: str
    target_level: str
    recommended_action: str
    start_date: date
    target_completion_date: date
    review_id: Optional[str] = None
    learning_resources: Optional[str] = None


class DevelopmentPlanResponse(BaseModel):
    plan_id: str
    employee_id: str
    competency_id: str
    current_level: str
    target_level: str
    recommended_action: str
    learning_resources: Optional[str]
    start_date: date
    target_completion_date: date
    status: str
    approval_status: str

    model_config = ConfigDict(from_attributes=True)


class PlanApprovalRequest(BaseModel):
    decision: str = "APPROVED"
    approval_role: str = "MANAGER"
    comments: Optional[str] = None


# Competency Schemas
class CompetencyResponse(BaseModel):
    competency_id: str
    category: str
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


# Anomaly Schemas
class AnomalyResponse(BaseModel):
    anomaly_id: str
    issue_type: str
    affected_entity: str
    affected_record_id: str
    severity: str
    description: str
    detection_status: str
    ground_truth_label: str
    expected_resolution: str
    detection_timestamp: datetime
    resolution_notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class AnomalyResolveRequest(BaseModel):
    resolution_status: str = "RESOLVED"
    resolution_notes: str


# Audit Schemas
class AuditEventResponse(BaseModel):
    event_id: str
    actor_id: Optional[str]
    entity_name: str
    entity_id: str
    operation_type: str
    old_values: Optional[Any]
    new_values: Optional[Any]
    reason: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
