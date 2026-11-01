from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from backend.generator.config import GeneratorConfig


def inject_anomalies(
    config: GeneratorConfig,
    employees: List[Dict[str, Any]],
    goals: List[Dict[str, Any]],
    key_results: List[Dict[str, Any]],
    feedbacks: List[Dict[str, Any]],
    competencies: List[Dict[str, Any]],
    review_cycles: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Injects deliberate anomalies adhering to the 5 required specifications:
    1. GOAL_OWNER_MISMATCH
    2. INVALID_PROGRESS
    3. INVALID_REVIEWER
    4. CLOSED_CYCLE_MODIFICATION
    5. UNTRACEABLE_FEEDBACK

    Returns:
    - anomalies: List of anomaly registry records for the database
    - ground_truth_records: List of entries for ground_truth.csv and ground_truth.json
    """
    anomalies = []
    ground_truth = []
    
    count_per_type = config.anomalies_per_type
    ano_idx = 1

    # 1. ANOMALY 1: GOAL_OWNER_MISMATCH
    # A goal references an employee different from its intended author/owner without delegation
    for i in range(1, count_per_type + 1):
        g_id = f"GOAL-ANOMALY-OWNER-{i:03d}"
        victim_emp = employees[i % len(employees)]
        mismatched_emp = employees[(i + 5) % len(employees)]
        
        anom_goal = {
            "goal_id": g_id,
            "employee_id": victim_emp["employee_id"],  # Wrongly linked owner
            "review_cycle_id": "CYCLE-2026-H1",
            "title": f"Strategic Initiative Allocated to Mismatched Owner {i}",
            "description": f"Goal intended for {mismatched_emp['department']} department delivery.",
            "category": "TECHNICAL",
            "priority": "HIGH",
            "start_date": "2026-01-01",
            "due_date": "2026-06-30",
            "weight": 1.0,
            "calculated_progress": 15.00,
            "status": "ACTIVE",
            "created_by": mismatched_emp["employee_id"],  # Mismatch: created by completely different owner
            "approved_by": None
        }
        goals.append(anom_goal)

        anom_id = f"ANO-{ano_idx:06d}"
        anomalies.append({
            "anomaly_id": anom_id,
            "issue_type": "GOAL_OWNER_MISMATCH",
            "affected_entity": "goals",
            "affected_record_id": g_id,
            "severity": "HIGH",
            "description": f"Goal {g_id} owner ({victim_emp['employee_id']}) diverges from intended creator ({mismatched_emp['employee_id']}) without delegation.",
            "detection_status": "DETECTED",
            "ground_truth_label": "ANOMALY_GOAL_OWNER_MISMATCH",
            "expected_resolution": f"Reassign goal to authentic creator {mismatched_emp['employee_id']} or invalidate record.",
        })
        ground_truth.append({
            "record_id": g_id,
            "entity_type": "goals",
            "issue_type": "GOAL_OWNER_MISMATCH",
            "expected_label": "ANOMALY_GOAL_OWNER_MISMATCH",
            "expected_decision": "REASSIGN_OR_QUARANTINE",
            "explanation": f"Discrepancy detected between goal owner {victim_emp['employee_id']} and author {mismatched_emp['employee_id']}."
        })
        ano_idx += 1

    # 2. ANOMALY 2: INVALID_PROGRESS
    # Progress exceeds the defined scale or deviates drastically from baseline, target, and current
    for i in range(1, count_per_type + 1):
        kr_id = f"KR-ANOMALY-PROG-{i:03d}"
        parent_goal = goals[i % len(goals)]
        
        anom_kr = {
            "key_result_id": kr_id,
            "goal_id": parent_goal["goal_id"],
            "metric_name": f"Anomalous Throughput Metric {i}",
            "metric_direction": "INCREASING",
            "baseline_value": 0.0,
            "target_value": 100.0,
            "current_value": 12.0,  # Computed should be 12.0%
            "unit": "PERCENT",
            "weight": 1.0,
            "progress_percentage": 285.50,  # Invalid: arbitrarily inflated progress
            "status": "ACHIEVED"
        }
        key_results.append(anom_kr)

        anom_id = f"ANO-{ano_idx:06d}"
        anomalies.append({
            "anomaly_id": anom_id,
            "issue_type": "INVALID_PROGRESS",
            "affected_entity": "key_results",
            "affected_record_id": kr_id,
            "severity": "CRITICAL",
            "description": f"Key Result {kr_id} reports progress 285.50% while formula computed progress is 12.00%.",
            "detection_status": "DETECTED",
            "ground_truth_label": "ANOMALY_INVALID_PROGRESS",
            "expected_resolution": "Trigger automated recalculation from baseline (0.0), target (100.0), and current (12.0).",
        })
        ground_truth.append({
            "record_id": kr_id,
            "entity_type": "key_results",
            "issue_type": "INVALID_PROGRESS",
            "expected_label": "ANOMALY_INVALID_PROGRESS",
            "expected_decision": "RECALCULATE_PROGRESS",
            "explanation": "Calculated progress percentage deviates from source observation formula by > 200%."
        })
        ano_idx += 1

    # 3. ANOMALY 3: INVALID_REVIEWER
    # A reviewer provides feedback without an eligible relationship to the employee
    for i in range(1, count_per_type + 1):
        fb_id = f"FB-ANOMALY-REV-{i:03d}"
        # Pick two employees from different departments with different managers
        subj_emp = employees[i % len(employees)]
        rev_emp = employees[(i + 15) % len(employees)]
        comp = competencies[0]

        anom_fb = {
            "feedback_id": fb_id,
            "subject_employee_id": subj_emp["employee_id"],
            "reviewer_employee_id": rev_emp["employee_id"],  # Ineligible reviewer
            "review_cycle_id": "CYCLE-2026-H1",
            "feedback_type": "PEER",
            "competency_id": comp["competency_id"],
            "rating": 4.50,
            "comments": "Great work on team tasks.",
            "submission_date": "2026-06-15",
            "status": "SUBMITTED"
        }
        feedbacks.append(anom_fb)

        anom_id = f"ANO-{ano_idx:06d}"
        anomalies.append({
            "anomaly_id": anom_id,
            "issue_type": "INVALID_REVIEWER",
            "affected_entity": "feedbacks",
            "affected_record_id": fb_id,
            "severity": "MEDIUM",
            "description": f"Feedback {fb_id} submitted by {rev_emp['employee_id']} who lacks eligible peer, managerial, or cross-functional relationship to {subj_emp['employee_id']}.",
            "detection_status": "DETECTED",
            "ground_truth_label": "ANOMALY_INVALID_REVIEWER",
            "expected_resolution": "Quarantine feedback and exclude from performance review scoring calibration.",
        })
        ground_truth.append({
            "record_id": fb_id,
            "entity_type": "feedbacks",
            "issue_type": "INVALID_REVIEWER",
            "expected_label": "ANOMALY_INVALID_REVIEWER",
            "expected_decision": "EXCLUDE_FROM_CALIBRATION",
            "explanation": f"Reviewer {rev_emp['employee_id']} does not satisfy eligibility criteria for subject {subj_emp['employee_id']}."
        })
        ano_idx += 1

    # 4. ANOMALY 4: CLOSED_CYCLE_MODIFICATION
    # A closed review cycle accepts a modification without an authorized correction event
    for i in range(1, count_per_type + 1):
        g_id = f"GOAL-ANOMALY-CLOSED-{i:03d}"
        emp = employees[i % len(employees)]

        anom_closed_goal = {
            "goal_id": g_id,
            "employee_id": emp["employee_id"],
            "review_cycle_id": "CYCLE-2025-H2",  # CLOSED cycle!
            "title": f"Unauthorized Modification in Closed Cycle {i}",
            "description": "Tampered goal inserted into finalized review cycle.",
            "category": "DELIVERY",
            "priority": "CRITICAL",
            "start_date": "2025-07-01",
            "due_date": "2025-12-31",
            "weight": 1.0,
            "calculated_progress": 100.00,
            "status": "ACTIVE",  # Should not be ACTIVE in closed cycle without audit correction
            "created_by": emp["employee_id"],
            "approved_by": emp["manager_id"] or emp["employee_id"]
        }
        goals.append(anom_closed_goal)

        anom_id = f"ANO-{ano_idx:06d}"
        anomalies.append({
            "anomaly_id": anom_id,
            "issue_type": "CLOSED_CYCLE_MODIFICATION",
            "affected_entity": "goals",
            "affected_record_id": g_id,
            "severity": "CRITICAL",
            "description": f"Goal {g_id} was modified/created in closed cycle CYCLE-2025-H2 without an authorized AuditEvent correction.",
            "detection_status": "DETECTED",
            "ground_truth_label": "ANOMALY_CLOSED_CYCLE_MODIFICATION",
            "expected_resolution": "Roll back modification to finalized snapshot and flag unauthorized actor.",
        })
        ground_truth.append({
            "record_id": g_id,
            "entity_type": "goals",
            "issue_type": "CLOSED_CYCLE_MODIFICATION",
            "expected_label": "ANOMALY_CLOSED_CYCLE_MODIFICATION",
            "expected_decision": "REVERT_TO_SNAPSHOT",
            "explanation": "Record modified in a closed cycle without required audit approval."
        })
        ano_idx += 1

    # 5. ANOMALY 5: UNTRACEABLE_FEEDBACK
    # Feedback exists without verifiable evidence or sufficient traceability metadata
    for i in range(1, count_per_type + 1):
        fb_id = f"FB-ANOMALY-UNTRACE-{i:03d}"
        subj_emp = employees[i % len(employees)]
        comp = competencies[1 % len(competencies)]

        anom_fb_untrace = {
            "feedback_id": fb_id,
            "subject_employee_id": subj_emp["employee_id"],
            "reviewer_employee_id": subj_emp["manager_id"] or "EMP-000001",
            "review_cycle_id": "CYCLE-2026-H1",
            "feedback_type": "MANAGER",
            "competency_id": comp["competency_id"],
            "rating": 1.00,  # Extreme rating
            "comments": "Poor.",  # Untraceable / insufficient justification (< 10 chars)
            "submission_date": "2026-06-15",
            "status": "SUBMITTED"
        }
        feedbacks.append(anom_fb_untrace)

        anom_id = f"ANO-{ano_idx:06d}"
        anomalies.append({
            "anomaly_id": anom_id,
            "issue_type": "UNTRACEABLE_FEEDBACK",
            "affected_entity": "feedbacks",
            "affected_record_id": fb_id,
            "severity": "MEDIUM",
            "description": f"Feedback {fb_id} has extreme rating (1.00) without substantive commentary or linked evidence.",
            "detection_status": "DETECTED",
            "ground_truth_label": "ANOMALY_UNTRACEABLE_FEEDBACK",
            "expected_resolution": "Flag feedback for evidentiary substantiation or discard prior to final calibration.",
        })
        ground_truth.append({
            "record_id": fb_id,
            "entity_type": "feedbacks",
            "issue_type": "UNTRACEABLE_FEEDBACK",
            "expected_label": "ANOMALY_UNTRACEABLE_FEEDBACK",
            "expected_decision": "REQUEST_EVIDENCE_OR_DISCARD",
            "explanation": "Extreme rating submitted without mandatory evidence link or descriptive commentary."
        })
        ano_idx += 1

    return anomalies, ground_truth
