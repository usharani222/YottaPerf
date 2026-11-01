import os
import json
import csv
from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationReport:
    total_records_validated: int = 0
    primary_key_violations: int = 0
    foreign_key_violations: int = 0
    invalid_date_sequences: int = 0
    invalid_enum_values: int = 0
    invalid_progress_calculations: int = 0
    weighted_score_mismatches: int = 0
    invalid_lifecycle_transitions: int = 0
    duplicate_records: int = 0
    circular_hierarchy_violations: int = 0
    detected_anomalies: int = 0
    ground_truth_mismatches: int = 0
    details: List[str] = field(default_factory=list)

    @property
    def overall_status(self) -> str:
        # Detected anomalies are expected when deliberate anomalies are injected,
        # but structural/referential violations on baseline should be 0.
        if (
            self.primary_key_violations == 0
            and self.foreign_key_violations == 0
            and self.invalid_date_sequences == 0
            and self.circular_hierarchy_violations == 0
            and self.duplicate_records == 0
            and self.ground_truth_mismatches == 0
        ):
            return "PASSED"
        return "FAILED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records_validated": self.total_records_validated,
            "primary_key_violations": self.primary_key_violations,
            "foreign_key_violations": self.foreign_key_violations,
            "invalid_date_sequences": self.invalid_date_sequences,
            "invalid_enum_values": self.invalid_enum_values,
            "invalid_progress_calculations": self.invalid_progress_calculations,
            "weighted_score_mismatches": self.weighted_score_mismatches,
            "invalid_lifecycle_transitions": self.invalid_lifecycle_transitions,
            "duplicate_records": self.duplicate_records,
            "circular_hierarchy_violations": self.circular_hierarchy_violations,
            "detected_anomalies": self.detected_anomalies,
            "ground_truth_mismatches": self.ground_truth_mismatches,
            "overall_validation_status": self.overall_status,
            "details_count": len(self.details),
        }


class ValidationEngine:
    """
    Automated Validation Engine executing comprehensive relational, business rule,
    and anomaly consistency audits across datasets and database entities.
    """

    def validate_dataset(
        self,
        tables_data: Dict[str, List[Dict[str, Any]]],
        ground_truth_records: Optional[List[Dict[str, Any]]] = None
    ) -> ValidationReport:
        report = ValidationReport()

        total_records = sum(len(v) for v in tables_data.values())
        report.total_records_validated = total_records

        # Primary Key mapping: table -> pk column
        pk_map = {
            "roles": "role_id",
            "competencies": "competency_id",
            "review_cycles": "cycle_id",
            "employees": "employee_id",
            "user_accounts": "user_id",
            "managers": "manager_id",
            "employee_manager_histories": "history_id",
            "goals": "goal_id",
            "key_results": "key_result_id",
            "goal_histories": "history_id",
            "check_ins": "check_in_id",
            "evidences": "evidence_id",
            "feedbacks": "feedback_id",
            "review_permissions": "permission_id",
            "reviews": "review_id",
            "review_histories": "history_id",
            "development_plans": "plan_id",
            "development_activities": "activity_id",
            "development_plan_approvals": "approval_id",
            "anomalies": "anomaly_id",
            "audit_events": "event_id",
        }

        # A. Primary Key Uniqueness
        for table, pk_col in pk_map.items():
            records = tables_data.get(table, [])
            seen_pks = set()
            for r in records:
                pk_val = r.get(pk_col)
                if not pk_val:
                    report.primary_key_violations += 1
                    report.details.append(f"Missing PK in table {table}")
                elif pk_val in seen_pks:
                    report.primary_key_violations += 1
                    report.details.append(f"Duplicate PK {pk_val} in table {table}")
                seen_pks.add(pk_val)

        # Pre-index valid PK sets for FK validation
        emp_ids = {e["employee_id"] for e in tables_data.get("employees", [])}
        goal_ids = {g["goal_id"] for g in tables_data.get("goals", [])}
        cycle_ids = {c["cycle_id"] for c in tables_data.get("review_cycles", [])}
        comp_ids = {c["competency_id"] for c in tables_data.get("competencies", [])}
        role_ids = {r["role_id"] for r in tables_data.get("roles", [])}

        # B. Foreign Key Integrity
        # 1. Employees manager_id
        for e in tables_data.get("employees", []):
            mgr_id = e.get("manager_id")
            if mgr_id and mgr_id not in emp_ids:
                report.foreign_key_violations += 1
                report.details.append(f"Invalid manager_id {mgr_id} on employee {e['employee_id']}")

        # 2. Employee roles
        for er in tables_data.get("employee_roles", []):
            if er["employee_id"] not in emp_ids:
                report.foreign_key_violations += 1
                report.details.append(f"Invalid employee_id {er['employee_id']} in employee_roles")
            if er["role_id"] not in role_ids:
                report.foreign_key_violations += 1
                report.details.append(f"Invalid role_id {er['role_id']} in employee_roles")

        # 3. Goals
        for g in tables_data.get("goals", []):
            if g["employee_id"] not in emp_ids:
                report.foreign_key_violations += 1
                report.details.append(f"Invalid employee_id {g['employee_id']} in goals")
            if g["review_cycle_id"] not in cycle_ids:
                report.foreign_key_violations += 1
                report.details.append(f"Invalid review_cycle_id {g['review_cycle_id']} in goals")

        # 4. Key Results
        for kr in tables_data.get("key_results", []):
            if kr["goal_id"] not in goal_ids:
                report.foreign_key_violations += 1
                report.details.append(f"Invalid goal_id {kr['goal_id']} in key_results")

        # 5. Feedbacks
        for fb in tables_data.get("feedbacks", []):
            if fb["subject_employee_id"] not in emp_ids:
                report.foreign_key_violations += 1
            if fb["reviewer_employee_id"] not in emp_ids:
                report.foreign_key_violations += 1
            if fb["review_cycle_id"] not in cycle_ids:
                report.foreign_key_violations += 1
            if fb["competency_id"] not in comp_ids:
                report.foreign_key_violations += 1

        # C. Allowed Enum Values
        valid_cycle_stages = {"UPCOMING", "OPEN", "EVALUATION", "CLOSED", "ARCHIVED"}
        for c in tables_data.get("review_cycles", []):
            if c.get("stage") not in valid_cycle_stages:
                report.invalid_enum_values += 1

        valid_goal_statuses = {"DRAFT", "SUBMITTED", "ACTIVE", "COMPLETED", "CANCELLED"}
        for g in tables_data.get("goals", []):
            if g.get("status") not in valid_goal_statuses:
                report.invalid_enum_values += 1

        valid_rev_stages = {
            "DRAFT", "SELF_REVIEW_PENDING", "MANAGER_REVIEW_PENDING",
            "HR_REVIEW_PENDING", "APPROVED", "COMPLETED", "REJECTED",
            "RETURNED_FOR_REVISION", "INCOMPLETE"
        }
        for r in tables_data.get("reviews", []):
            if r.get("stage") not in valid_rev_stages:
                report.invalid_enum_values += 1

        # D. Date Ordering
        for c in tables_data.get("review_cycles", []):
            if str(c["end_date"]) <= str(c["start_date"]):
                report.invalid_date_sequences += 1
                report.details.append(f"Cycle {c['cycle_id']} end_date <= start_date")

        for g in tables_data.get("goals", []):
            if str(g["due_date"]) < str(g["start_date"]):
                report.invalid_date_sequences += 1
                report.details.append(f"Goal {g['goal_id']} due_date < start_date")

        for dp in tables_data.get("development_plans", []):
            if str(dp["target_completion_date"]) < str(dp["start_date"]):
                report.invalid_date_sequences += 1
                report.details.append(f"Plan {dp['plan_id']} target_date < start_date")

        # G. Manager Hierarchy Consistency (Cycle Detection)
        emp_parent_map = {e["employee_id"]: e.get("manager_id") for e in tables_data.get("employees", [])}
        for emp_id in emp_parent_map.keys():
            visited = set()
            curr = emp_id
            while curr:
                if curr in visited:
                    report.circular_hierarchy_violations += 1
                    report.details.append(f"Circular hierarchy involving {curr}")
                    break
                visited.add(curr)
                curr = emp_parent_map.get(curr)

        # H. Duplicate Composite Records
        # Composite unique check: reviews (employee_id, review_cycle_id)
        seen_reviews = set()
        for r in tables_data.get("reviews", []):
            key = (r["employee_id"], r["review_cycle_id"])
            if key in seen_reviews:
                report.duplicate_records += 1
                report.details.append(f"Duplicate review for employee {key[0]} in cycle {key[1]}")
            seen_reviews.add(key)

        # Composite unique check: employee_roles (employee_id, role_id)
        seen_emp_roles = set()
        for er in tables_data.get("employee_roles", []):
            key = (er["employee_id"], er["role_id"])
            if key in seen_emp_roles:
                report.duplicate_records += 1
            seen_emp_roles.add(key)

        # I & J. Progress Calculation & Weighted Score Reconciliation
        # Check Key Results formula calculations
        anom_kr_ids = {a["affected_record_id"] for a in tables_data.get("anomalies", []) if a["affected_entity"] == "key_results"}
        for kr in tables_data.get("key_results", []):
            kr_id = kr["key_result_id"]
            if kr_id in anom_kr_ids:
                # Injected anomaly detected
                report.detected_anomalies += 1
                continue

            base = float(kr["baseline_value"])
            targ = float(kr["target_value"])
            curr = float(kr["current_value"])
            direction = kr["metric_direction"]

            if direction == "INCREASING":
                expected = ((curr - base) / (targ - base)) * 100.0 if abs(targ - base) > 1e-9 else 100.0
            else:
                expected = ((base - curr) / (base - targ)) * 100.0 if abs(base - targ) > 1e-9 else 100.0
            expected = round(max(0.0, expected), 2)
            actual = round(float(kr["progress_percentage"]), 2)

            if abs(expected - actual) > 0.05:
                report.invalid_progress_calculations += 1
                report.details.append(f"Progress mismatch on KR {kr_id}: expected {expected}, got {actual}")

        # Check Review Final Score Weighted Reconciliation
        cycle_weights = {
            c["cycle_id"]: (float(c["goal_weight"]) / 100.0, float(c["competency_weight"]) / 100.0, float(c["feedback_weight"]) / 100.0)
            for c in tables_data.get("review_cycles", [])
        }
        for rev in tables_data.get("reviews", []):
            weights = cycle_weights.get(rev["review_cycle_id"], (0.5, 0.3, 0.2))
            expected_final = round(
                (float(rev["goal_score"]) * weights[0]) +
                (float(rev["competency_score"]) * weights[1]) +
                (float(rev["feedback_score"]) * weights[2]),
                2
            )
            actual_final = round(float(rev["final_score"]), 2)
            if abs(expected_final - actual_final) > 0.05:
                report.weighted_score_mismatches += 1
                report.details.append(f"Score mismatch on Review {rev['review_id']}: expected {expected_final}, got {actual_final}")

        # O. Anomaly and Ground-Truth Consistency
        anomalies_list = tables_data.get("anomalies", [])
        report.detected_anomalies += len(anomalies_list)

        if ground_truth_records:
            gt_record_ids = {g["record_id"] for g in ground_truth_records}
            ano_record_ids = {a["affected_record_id"] for a in anomalies_list}

            # Check that every ground truth record corresponds to an affected anomaly record
            diff1 = gt_record_ids - ano_record_ids
            diff2 = ano_record_ids - gt_record_ids
            if diff1 or diff2:
                report.ground_truth_mismatches += len(diff1) + len(diff2)
                report.details.append(f"Ground truth mismatches: GT extra={diff1}, Ano extra={diff2}")

        return report
