export interface UserProfile {
  user_id: string;
  employee_id: string;
  username: string;
  email: string;
  full_name: string;
  department: string;
  job_title: string;
  roles: string[];
}

export interface Employee {
  employee_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  department: string;
  job_title: string;
  job_level: string;
  manager_id?: string | null;
  is_active: boolean;
  hire_date: string;
}

export interface HierarchyNode {
  id: string;
  name: string;
  title: string;
  department: string;
  level: string;
  manager_id?: string | null;
  children: HierarchyNode[];
}

export interface ReviewCycle {
  cycle_id: string;
  cycle_name: string;
  start_date: string;
  end_date: string;
  submission_deadline: string;
  stage: string;
  goal_weight: number;
  competency_weight: number;
  feedback_weight: number;
}

export interface KeyResult {
  key_result_id: string;
  goal_id: string;
  metric_name: string;
  metric_direction: 'INCREASING' | 'DECREASING';
  baseline_value: number;
  target_value: number;
  current_value: number;
  unit: string;
  weight: number;
  progress_percentage: number;
  status: string;
}

export interface Goal {
  goal_id: string;
  employee_id: string;
  review_cycle_id: string;
  title: string;
  description?: string;
  category: string;
  priority: string;
  start_date: string;
  due_date: string;
  weight: number;
  calculated_progress: number;
  status: string;
  created_by: string;
  approved_by?: string;
  key_results: KeyResult[];
}

export interface GoalHistory {
  history_id: string;
  goal_id: string;
  version_number: number;
  title: string;
  status: string;
  calculated_progress: number;
  changed_by: string;
  change_reason: string;
  changed_at: string;
}

export interface Evidence {
  evidence_id: string;
  evidence_type: string;
  reference_url: string;
  description: string;
  verification_status: string;
}

export interface CheckIn {
  check_in_id: string;
  employee_id: string;
  goal_id: string;
  review_cycle_id: string;
  check_in_date: string;
  progress_update: number;
  employee_comments: string;
  manager_comments?: string;
  blockers?: string;
  next_steps?: string;
  evidences?: Evidence[];
}

export interface Feedback {
  feedback_id: string;
  subject_employee_id: string;
  reviewer_employee_id: string;
  review_cycle_id: string;
  feedback_type: string;
  competency_id: string;
  rating: number;
  comments: string;
  submission_date: string;
  status: string;
}

export interface Review {
  review_id: string;
  employee_id: string;
  review_cycle_id: string;
  goal_score: number;
  competency_score: number;
  feedback_score: number;
  final_score: number;
  rating_category: string;
  stage: string;
  self_comments?: string;
  manager_comments?: string;
  hr_comments?: string;
}

export interface Competency {
  competency_id: string;
  category: string;
  name: string;
  description: string;
}

export interface DevelopmentPlan {
  plan_id: string;
  employee_id: string;
  competency_id: string;
  current_level: string;
  target_level: string;
  recommended_action: string;
  learning_resources?: string;
  start_date: string;
  target_completion_date: string;
  status: string;
  approval_status: string;
}

export interface Anomaly {
  anomaly_id: string;
  issue_type: string;
  affected_entity: string;
  affected_record_id: string;
  severity: string;
  description: string;
  detection_status: string;
  ground_truth_label: string;
  expected_resolution: string;
  detection_timestamp: string;
  resolution_notes?: string;
}

export interface AuditEvent {
  event_id: string;
  actor_id?: string;
  entity_name: string;
  entity_id: string;
  operation_type: string;
  old_values?: any;
  new_values?: any;
  reason?: string;
  timestamp: string;
}

export interface DashboardKPIs {
  total_employees: number;
  total_managers: number;
  active_review_cycles: number;
  total_goals: number;
  average_goal_progress: number;
  completed_reviews: number;
  pending_reviews: number;
  development_plans_in_progress: number;
  open_anomalies: number;
}
