-- YottaPerf Normalized Relational Database Schema (PostgreSQL)
-- Implements third normal form (3NF), strict foreign keys, check constraints,
-- deterministic ID conventions, and immutable audit structures.

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS audit_events CASCADE;
DROP TABLE IF EXISTS anomalies CASCADE;
DROP TABLE IF EXISTS development_plan_approvals CASCADE;
DROP TABLE IF EXISTS development_activities CASCADE;
DROP TABLE IF EXISTS development_plans CASCADE;
DROP TABLE IF EXISTS review_histories CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS review_permissions CASCADE;
DROP TABLE IF EXISTS feedback_evidence CASCADE;
DROP TABLE IF EXISTS feedbacks CASCADE;
DROP TABLE IF EXISTS evidences CASCADE;
DROP TABLE IF EXISTS check_ins CASCADE;
DROP TABLE IF EXISTS goal_histories CASCADE;
DROP TABLE IF EXISTS key_results CASCADE;
DROP TABLE IF EXISTS goals CASCADE;
DROP TABLE IF EXISTS competencies CASCADE;
DROP TABLE IF EXISTS review_cycles CASCADE;
DROP TABLE IF EXISTS employee_manager_histories CASCADE;
DROP TABLE IF EXISTS managers CASCADE;
DROP TABLE IF EXISTS user_accounts CASCADE;
DROP TABLE IF EXISTS employee_roles CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS employees CASCADE;

-- 1. ROLES
CREATE TABLE roles (
    role_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. EMPLOYEES
CREATE TABLE employees (
    employee_id VARCHAR(32) PRIMARY KEY, -- Deterministic ID: EMP-000001
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_level VARCHAR(20) NOT NULL,
    manager_id VARCHAR(32) REFERENCES employees(employee_id) ON DELETE RESTRICT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    hire_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_manager_id ON employees(manager_id);
CREATE INDEX idx_employees_is_active ON employees(is_active);

-- 3. EMPLOYEE_ROLES (Bridge)
CREATE TABLE employee_roles (
    employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    role_id VARCHAR(32) NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (employee_id, role_id)
);

-- 4. USER_ACCOUNTS
CREATE TABLE user_accounts (
    user_id VARCHAR(32) PRIMARY KEY, -- USR-000001
    employee_id VARCHAR(32) UNIQUE NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ
);

-- 5. MANAGERS
CREATE TABLE managers (
    manager_id VARCHAR(32) PRIMARY KEY, -- MGR-000001
    employee_id VARCHAR(32) UNIQUE NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    management_level VARCHAR(50) NOT NULL,
    budget_authority NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. EMPLOYEE_MANAGER_HISTORIES
CREATE TABLE employee_manager_histories (
    history_id VARCHAR(32) PRIMARY KEY, -- EMH-000001
    employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    manager_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    transfer_reason VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_emh_dates CHECK (effective_end_date IS NULL OR effective_end_date >= effective_start_date)
);

CREATE INDEX idx_emh_emp ON employee_manager_histories(employee_id);

-- 7. REVIEW_CYCLES
CREATE TABLE review_cycles (
    cycle_id VARCHAR(32) PRIMARY KEY, -- CYCLE-2026-H1
    cycle_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    submission_deadline DATE NOT NULL,
    stage VARCHAR(50) NOT NULL DEFAULT 'UPCOMING',
    goal_weight NUMERIC(5, 2) NOT NULL DEFAULT 50.00,
    competency_weight NUMERIC(5, 2) NOT NULL DEFAULT 30.00,
    feedback_weight NUMERIC(5, 2) NOT NULL DEFAULT 20.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cycle_dates CHECK (end_date > start_date),
    CONSTRAINT chk_cycle_weights CHECK (goal_weight + competency_weight + feedback_weight = 100.00),
    CONSTRAINT chk_cycle_stage CHECK (stage IN ('UPCOMING', 'OPEN', 'EVALUATION', 'CLOSED', 'ARCHIVED'))
);

-- 8. COMPETENCIES
CREATE TABLE competencies (
    competency_id VARCHAR(32) PRIMARY KEY, -- COMP-001
    category VARCHAR(100) NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. GOALS
CREATE TABLE goals (
    goal_id VARCHAR(64) PRIMARY KEY, -- GOAL-EMP-000001-001
    employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    review_cycle_id VARCHAR(32) NOT NULL REFERENCES review_cycles(cycle_id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    start_date DATE NOT NULL,
    due_date DATE NOT NULL,
    weight NUMERIC(5, 2) NOT NULL DEFAULT 1.00,
    calculated_progress NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    created_by VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    approved_by VARCHAR(32) REFERENCES employees(employee_id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_goal_dates CHECK (due_date >= start_date),
    CONSTRAINT chk_goal_weight CHECK (weight > 0),
    CONSTRAINT chk_goal_status CHECK (status IN ('DRAFT', 'SUBMITTED', 'ACTIVE', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT chk_goal_priority CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE INDEX idx_goals_emp ON goals(employee_id);
CREATE INDEX idx_goals_cycle ON goals(review_cycle_id);
CREATE INDEX idx_goals_status ON goals(status);

-- 10. KEY_RESULTS
CREATE TABLE key_results (
    key_result_id VARCHAR(64) PRIMARY KEY, -- KR-GOAL-EMP-000001-001-01
    goal_id VARCHAR(64) NOT NULL REFERENCES goals(goal_id) ON DELETE CASCADE,
    metric_name VARCHAR(200) NOT NULL,
    metric_direction VARCHAR(20) NOT NULL DEFAULT 'INCREASING',
    baseline_value NUMERIC(12, 2) NOT NULL,
    target_value NUMERIC(12, 2) NOT NULL,
    current_value NUMERIC(12, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    weight NUMERIC(5, 2) NOT NULL DEFAULT 1.00,
    progress_percentage NUMERIC(6, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(50) NOT NULL DEFAULT 'ON_TRACK',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_kr_direction CHECK (metric_direction IN ('INCREASING', 'DECREASING')),
    CONSTRAINT chk_kr_weight CHECK (weight > 0),
    CONSTRAINT chk_kr_status CHECK (status IN ('ON_TRACK', 'AT_RISK', 'BEHIND', 'ACHIEVED'))
);

CREATE INDEX idx_kr_goal ON key_results(goal_id);

-- 11. GOAL_HISTORIES
CREATE TABLE goal_histories (
    history_id VARCHAR(32) PRIMARY KEY, -- GH-000001
    goal_id VARCHAR(64) NOT NULL REFERENCES goals(goal_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    calculated_progress NUMERIC(5, 2) NOT NULL,
    changed_by VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    change_reason VARCHAR(255) NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gh_goal ON goal_histories(goal_id);

-- 12. CHECK_INS
CREATE TABLE check_ins (
    check_in_id VARCHAR(32) PRIMARY KEY, -- CHK-000001
    employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    goal_id VARCHAR(64) NOT NULL REFERENCES goals(goal_id) ON DELETE RESTRICT,
    review_cycle_id VARCHAR(32) NOT NULL REFERENCES review_cycles(cycle_id) ON DELETE RESTRICT,
    check_in_date DATE NOT NULL,
    progress_update NUMERIC(5, 2) NOT NULL,
    employee_comments TEXT NOT NULL,
    manager_comments TEXT,
    blockers TEXT,
    next_steps TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_checkins_emp ON check_ins(employee_id);
CREATE INDEX idx_checkins_goal ON check_ins(goal_id);

-- 13. EVIDENCES
CREATE TABLE evidences (
    evidence_id VARCHAR(32) PRIMARY KEY, -- EVD-000001
    check_in_id VARCHAR(32) REFERENCES check_ins(check_in_id) ON DELETE SET NULL,
    evidence_type VARCHAR(50) NOT NULL,
    reference_url VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    uploaded_by VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    uploaded_date DATE NOT NULL,
    verification_status VARCHAR(30) NOT NULL DEFAULT 'VERIFIED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_evd_status CHECK (verification_status IN ('VERIFIED', 'PENDING_REVIEW', 'REJECTED'))
);

CREATE INDEX idx_evd_checkin ON evidences(check_in_id);

-- 14. FEEDBACKS
CREATE TABLE feedbacks (
    feedback_id VARCHAR(32) PRIMARY KEY, -- FB-000001
    subject_employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    reviewer_employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    review_cycle_id VARCHAR(32) NOT NULL REFERENCES review_cycles(cycle_id) ON DELETE RESTRICT,
    feedback_type VARCHAR(30) NOT NULL,
    competency_id VARCHAR(32) NOT NULL REFERENCES competencies(competency_id) ON DELETE RESTRICT,
    rating NUMERIC(3, 2) NOT NULL,
    comments TEXT NOT NULL,
    submission_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_fb_type CHECK (feedback_type IN ('SELF', 'MANAGER', 'PEER')),
    CONSTRAINT chk_fb_rating CHECK (rating >= 1.00 AND rating <= 5.00),
    CONSTRAINT chk_fb_status CHECK (status IN ('DRAFT', 'SUBMITTED', 'REVISED'))
);

CREATE INDEX idx_fb_subject ON feedbacks(subject_employee_id);
CREATE INDEX idx_fb_reviewer ON feedbacks(reviewer_employee_id);
CREATE INDEX idx_fb_cycle ON feedbacks(review_cycle_id);

-- 15. FEEDBACK_EVIDENCE (Bridge)
CREATE TABLE feedback_evidence (
    feedback_id VARCHAR(32) NOT NULL REFERENCES feedbacks(feedback_id) ON DELETE CASCADE,
    evidence_id VARCHAR(32) NOT NULL REFERENCES evidences(evidence_id) ON DELETE CASCADE,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (feedback_id, evidence_id)
);

-- 16. REVIEW_PERMISSIONS (Bridge)
CREATE TABLE review_permissions (
    permission_id VARCHAR(32) PRIMARY KEY, -- RP-000001
    review_cycle_id VARCHAR(32) NOT NULL REFERENCES review_cycles(cycle_id) ON DELETE CASCADE,
    subject_employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    reviewer_employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
    relationship_type VARCHAR(30) NOT NULL,
    granted_by VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (review_cycle_id, subject_employee_id, reviewer_employee_id)
);

-- 17. REVIEWS
CREATE TABLE reviews (
    review_id VARCHAR(32) PRIMARY KEY, -- REV-2026-000001
    employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    review_cycle_id VARCHAR(32) NOT NULL REFERENCES review_cycles(cycle_id) ON DELETE RESTRICT,
    goal_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    competency_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    feedback_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    final_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    rating_category VARCHAR(50) NOT NULL DEFAULT 'MEETS_EXPECTATIONS',
    stage VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    self_comments TEXT,
    manager_comments TEXT,
    hr_comments TEXT,
    self_submitted_at TIMESTAMPTZ,
    manager_approved_at TIMESTAMPTZ,
    hr_approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (employee_id, review_cycle_id),
    CONSTRAINT chk_rev_stage CHECK (stage IN (
        'DRAFT', 'SELF_REVIEW_PENDING', 'MANAGER_REVIEW_PENDING',
        'HR_REVIEW_PENDING', 'APPROVED', 'COMPLETED',
        'REJECTED', 'RETURNED_FOR_REVISION', 'INCOMPLETE'
    )),
    CONSTRAINT chk_rev_rating CHECK (rating_category IN (
        'NEEDS_IMPROVEMENT', 'MEETS_EXPECTATIONS', 'EXCEEDS_EXPECTATIONS', 'OUTSTANDING'
    ))
);

CREATE INDEX idx_reviews_emp ON reviews(employee_id);
CREATE INDEX idx_reviews_cycle ON reviews(review_cycle_id);
CREATE INDEX idx_reviews_stage ON reviews(stage);

-- 18. REVIEW_HISTORIES
CREATE TABLE review_histories (
    history_id VARCHAR(32) PRIMARY KEY, -- RH-000001
    review_id VARCHAR(32) NOT NULL REFERENCES reviews(review_id) ON DELETE CASCADE,
    previous_stage VARCHAR(50) NOT NULL,
    new_stage VARCHAR(50) NOT NULL,
    changed_by VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    comments TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rh_review ON review_histories(review_id);

-- 19. DEVELOPMENT_PLANS
CREATE TABLE development_plans (
    plan_id VARCHAR(32) PRIMARY KEY, -- DP-000001
    employee_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    review_id VARCHAR(32) REFERENCES reviews(review_id) ON DELETE SET NULL,
    competency_id VARCHAR(32) NOT NULL REFERENCES competencies(competency_id) ON DELETE RESTRICT,
    current_level VARCHAR(50) NOT NULL,
    target_level VARCHAR(50) NOT NULL,
    recommended_action TEXT NOT NULL,
    learning_resources TEXT,
    start_date DATE NOT NULL,
    target_completion_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'IN_PROGRESS',
    approval_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dp_dates CHECK (target_completion_date >= start_date),
    CONSTRAINT chk_dp_status CHECK (status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT chk_dp_approval CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED'))
);

CREATE INDEX idx_dp_emp ON development_plans(employee_id);

-- 20. DEVELOPMENT_ACTIVITIES
CREATE TABLE development_activities (
    activity_id VARCHAR(32) PRIMARY KEY, -- DA-000001
    plan_id VARCHAR(32) NOT NULL REFERENCES development_plans(plan_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    resource_url VARCHAR(500),
    status VARCHAR(30) NOT NULL DEFAULT 'NOT_STARTED',
    completed_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_da_status CHECK (status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED'))
);

-- 21. DEVELOPMENT_PLAN_APPROVALS
CREATE TABLE development_plan_approvals (
    approval_id VARCHAR(32) PRIMARY KEY, -- DPA-000001
    plan_id VARCHAR(32) NOT NULL REFERENCES development_plans(plan_id) ON DELETE CASCADE,
    approver_id VARCHAR(32) NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    approval_role VARCHAR(30) NOT NULL,
    decision VARCHAR(20) NOT NULL,
    comments TEXT,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dpa_decision CHECK (decision IN ('APPROVED', 'REJECTED', 'REQUESTED_CHANGES'))
);

-- 22. ANOMALIES
CREATE TABLE anomalies (
    anomaly_id VARCHAR(32) PRIMARY KEY, -- ANO-000001
    issue_type VARCHAR(50) NOT NULL,
    affected_entity VARCHAR(50) NOT NULL,
    affected_record_id VARCHAR(64) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    detection_status VARCHAR(30) NOT NULL DEFAULT 'DETECTED',
    ground_truth_label VARCHAR(50) NOT NULL,
    expected_resolution TEXT NOT NULL,
    detection_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_by VARCHAR(32) REFERENCES employees(employee_id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    CONSTRAINT chk_ano_severity CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    CONSTRAINT chk_ano_status CHECK (detection_status IN ('DETECTED', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE'))
);

CREATE INDEX idx_anomalies_status ON anomalies(detection_status);
CREATE INDEX idx_anomalies_type ON anomalies(issue_type);

-- 23. AUDIT_EVENTS
CREATE TABLE audit_events (
    event_id VARCHAR(32) PRIMARY KEY, -- AUD-000001
    actor_id VARCHAR(32) REFERENCES employees(employee_id) ON DELETE SET NULL,
    entity_name VARCHAR(50) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    operation_type VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    review_cycle_id VARCHAR(32) REFERENCES review_cycles(cycle_id) ON DELETE SET NULL,
    reason VARCHAR(255),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_audit_op CHECK (operation_type IN ('CREATE', 'UPDATE', 'DELETE', 'TRANSITION', 'CORRECTION'))
);

CREATE INDEX idx_audit_entity ON audit_events(entity_name, entity_id);
CREATE INDEX idx_audit_timestamp ON audit_events(timestamp);

-- Reference Roles Seeding
INSERT INTO roles (role_id, name, description) VALUES
('ROLE-EMP', 'EMPLOYEE', 'Standard employee access: own goals, check-ins, self-review'),
('ROLE-MGR', 'MANAGER', 'Managerial access: direct reports, approvals, team reviews'),
('ROLE-HR', 'HR_PARTNER', 'HR partner: cycle management, calibration, organizational oversight'),
('ROLE-OPS', 'IT_OPS', 'Operations & IT: synthetic generation, validation, system monitoring'),
('ROLE-ADM', 'ADMIN', 'System administrator: full configuration and security administration')
ON CONFLICT (role_id) DO NOTHING;
