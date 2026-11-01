from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple


def generate_event_histories(
    goals: List[Dict[str, Any]],
    reviews: List[Dict[str, Any]],
    employees: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates historical audit trails:
    - GoalHistory for goals
    - ReviewHistory for reviews
    - AuditEvent for system transactions
    """
    goal_histories = []
    review_histories = []
    audit_events = []

    gh_counter = 1
    rh_counter = 1
    aud_counter = 1

    # 1. Goal Histories (initial creation + active transition)
    for g in goals:
        emp_id = g["employee_id"]
        # Version 1: DRAFT
        goal_histories.append({
            "history_id": f"GH-{gh_counter:06d}",
            "goal_id": g["goal_id"],
            "version_number": 1,
            "title": g["title"],
            "status": "DRAFT",
            "calculated_progress": 0.00,
            "changed_by": emp_id,
            "change_reason": "Initial Goal Proposal Creation",
        })
        gh_counter += 1

        # Version 2: Current Status
        if g["status"] != "DRAFT":
            goal_histories.append({
                "history_id": f"GH-{gh_counter:06d}",
                "goal_id": g["goal_id"],
                "version_number": 2,
                "title": g["title"],
                "status": g["status"],
                "calculated_progress": g["calculated_progress"],
                "changed_by": g["approved_by"] or emp_id,
                "change_reason": "Manager Milestone Approval and Activation",
            })
            gh_counter += 1

    # 2. Review Histories
    for r in reviews:
        emp_id = r["employee_id"]
        review_histories.append({
            "history_id": f"RH-{rh_counter:06d}",
            "review_id": r["review_id"],
            "previous_stage": "DRAFT",
            "new_stage": "SELF_REVIEW_PENDING",
            "changed_by": emp_id,
            "comments": "Self assessment initiated."
        })
        rh_counter += 1

        if r["stage"] in ("APPROVED", "COMPLETED"):
            review_histories.append({
                "history_id": f"RH-{rh_counter:06d}",
                "review_id": r["review_id"],
                "previous_stage": "SELF_REVIEW_PENDING",
                "new_stage": r["stage"],
                "changed_by": "EMP-000001",  # Admin or HR
                "comments": "Final review score calibrated and approved."
            })
            rh_counter += 1

    # 3. Audit Events
    sample_size = min(len(goals), 50)
    for idx in range(sample_size):
        target_goal = goals[idx]
        audit_events.append({
            "event_id": f"AUD-{aud_counter:06d}",
            "actor_id": target_goal["employee_id"],
            "entity_name": "GOAL",
            "entity_id": target_goal["goal_id"],
            "operation_type": "CREATE",
            "old_values": None,
            "new_values": {"title": target_goal["title"], "status": target_goal["status"]},
            "review_cycle_id": target_goal["review_cycle_id"],
            "reason": "OKR Establishment",
        })
        aud_counter += 1

    return goal_histories, review_histories, audit_events
