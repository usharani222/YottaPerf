from datetime import date, timedelta
from typing import List, Dict, Any, Tuple
import random
from backend.generator.config import GeneratorConfig


def calculate_key_result_progress(
    metric_direction: str,
    baseline: float,
    target: float,
    current: float
) -> float:
    """
    Computes Key Result progress strictly from source values.
    Handles zero denominator, metric directions, and boundary clipping.
    """
    if metric_direction == "INCREASING":
        denominator = target - baseline
        if abs(denominator) < 1e-9:
            return 100.0 if current >= target else 0.0
        progress = ((current - baseline) / denominator) * 100.0
    else:  # DECREASING
        denominator = baseline - target
        if abs(denominator) < 1e-9:
            return 100.0 if current <= target else 0.0
        progress = ((baseline - current) / denominator) * 100.0

    # Normal bounds: clamp lower at 0.0%, allow realistic stretch up to 150.0%
    if progress < 0.0:
        return 0.0
    return round(progress, 2)


def generate_goals_and_key_results(
    config: GeneratorConfig,
    employees: List[Dict[str, Any]],
    review_cycles: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates goals and derived key results using deterministic source calculations.
    """
    goals = []
    key_results = []

    goal_templates = [
        ("Improve System Latency & P99 Response Time", "TECHNICAL", "DECREASING", "MS", 250.0, 100.0),
        ("Increase Automated Test Code Coverage", "TECHNICAL", "INCREASING", "PERCENT", 65.0, 90.0),
        ("Deliver Enterprise SSO & RBAC Module", "DELIVERY", "INCREASING", "PERCENT", 0.0, 100.0),
        ("Reduce Customer Onboarding Churn Rate", "CUSTOMER", "DECREASING", "PERCENT", 12.0, 4.0),
        ("Expand Strategic Enterprise Pipeline Value", "DELIVERY", "INCREASING", "USD", 100000.0, 500000.0),
        ("Publish Internal Architecture Tech Radars", "LEADERSHIP", "INCREASING", "COUNT", 0.0, 4.0),
        ("Conduct Engineering Mentorship Cohorts", "LEADERSHIP", "INCREASING", "COUNT", 0.0, 6.0),
        ("Automate Database Migration & Backup Drills", "TECHNICAL", "INCREASING", "PERCENT", 20.0, 100.0),
        ("Resolve High-Priority Security CVEs within SLA", "TECHNICAL", "INCREASING", "PERCENT", 50.0, 100.0),
        ("Optimize Cloud Compute & Infrastructure Spend", "DELIVERY", "DECREASING", "USD", 40000.0, 25000.0)
    ]

    total_goals = config.num_goals
    num_emps = len(employees)
    active_cycle_id = "CYCLE-2026-H1"
    closed_cycle_id = "CYCLE-2025-H2"

    for g_idx in range(1, total_goals + 1):
        emp = employees[(g_idx - 1) % num_emps]
        emp_id = emp["employee_id"]
        # Alternate cycles: 40% closed cycle, 60% active cycle
        cycle_id = closed_cycle_id if (g_idx % 5 < 2) else active_cycle_id
        
        goal_id = f"GOAL-{emp_id}-{g_idx:03d}"
        tpl = goal_templates[g_idx % len(goal_templates)]
        title = f"{tpl[0]} (Q{(g_idx % 4) + 1})"
        category = tpl[1]
        priority = ["LOW", "MEDIUM", "HIGH", "CRITICAL"][g_idx % 4]
        
        start_date = "2025-07-01" if cycle_id == closed_cycle_id else "2026-01-01"
        due_date = "2025-12-31" if cycle_id == closed_cycle_id else "2026-06-30"
        
        # Generate 2 to 3 Key Results for this goal
        kr_count = 2 + (g_idx % 2)
        goal_krs = []
        
        for k_idx in range(1, kr_count + 1):
            kr_id = f"KR-{goal_id}-{k_idx:02d}"
            direction = tpl[2]
            unit = tpl[3]
            base_val = tpl[4]
            targ_val = tpl[5]
            
            # Progress variance depending on cycle status
            if cycle_id == closed_cycle_id:
                # Closed cycle: realistic completion distributions (70% - 110%)
                ratio = 0.75 + (0.35 * rng.random())
            else:
                # Active cycle: in progress (20% - 90%)
                ratio = 0.20 + (0.75 * rng.random())
            
            if direction == "INCREASING":
                curr_val = round(base_val + (targ_val - base_val) * ratio, 2)
            else:
                curr_val = round(base_val - (base_val - targ_val) * ratio, 2)
            
            kr_prog = calculate_key_result_progress(direction, base_val, targ_val, curr_val)
            
            if kr_prog >= 100.0:
                kr_status = "ACHIEVED"
            elif kr_prog >= 70.0:
                kr_status = "ON_TRACK"
            elif kr_prog >= 40.0:
                kr_status = "AT_RISK"
            else:
                kr_status = "BEHIND"
                
            kr_weight = 1.0 + (k_idx * 0.5)
            
            kr_record = {
                "key_result_id": kr_id,
                "goal_id": goal_id,
                "metric_name": f"{tpl[0]} Metric {k_idx}",
                "metric_direction": direction,
                "baseline_value": base_val,
                "target_value": targ_val,
                "current_value": curr_val,
                "unit": unit,
                "weight": kr_weight,
                "progress_percentage": kr_prog,
                "status": kr_status,
            }
            key_results.append(kr_record)
            goal_krs.append(kr_record)

        # Reconcile Goal Progress from weighted Key Results
        total_kr_weight = sum(k["weight"] for k in goal_krs)
        weighted_progress_sum = sum(k["progress_percentage"] * k["weight"] for k in goal_krs)
        goal_progress = round(weighted_progress_sum / total_kr_weight, 2) if total_kr_weight > 0 else 0.0

        if cycle_id == closed_cycle_id:
            goal_status = "COMPLETED" if goal_progress >= 90.0 else "ACTIVE"
        else:
            goal_status = "ACTIVE" if goal_progress > 0 else "SUBMITTED"

        goal_record = {
            "goal_id": goal_id,
            "employee_id": emp_id,
            "review_cycle_id": cycle_id,
            "title": title,
            "description": f"Targeted objective for {emp['department']} department delivery.",
            "category": category,
            "priority": priority,
            "start_date": start_date,
            "due_date": due_date,
            "weight": 1.0,
            "calculated_progress": goal_progress,
            "status": goal_status,
            "created_by": emp_id,
            "approved_by": emp["manager_id"] or emp_id,
        }
        goals.append(goal_record)

    return goals, key_results


def generate_check_ins_and_evidences(
    config: GeneratorConfig,
    goals: List[Dict[str, Any]],
    employees: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates periodic check-ins and evidence artifacts.
    """
    check_ins = []
    evidences = []

    total_checkins = config.num_checkins
    emp_map = {e["employee_id"]: e for e in employees}
    
    evidence_types = ["CODE_PR", "METRIC_DASHBOARD", "CUSTOMER_EMAIL", "CERTIFICATION", "DOCUMENT"]
    
    for c_idx in range(1, total_checkins + 1):
        chk_id = f"CHK-{c_idx:06d}"
        target_goal = goals[(c_idx - 1) % len(goals)]
        emp = emp_map[target_goal["employee_id"]]
        
        cycle_id = target_goal["review_cycle_id"]
        base_year = 2025 if "2025" in cycle_id else 2026
        month = 1 + (c_idx % 6)
        day = 1 + (c_idx % 25)
        chk_date = f"{base_year}-{month:02d}-{day:02d}"
        
        progress_snapshot = min(100.0, round(float(target_goal["calculated_progress"]) * (0.3 + (0.7 * (c_idx % 10) / 10)), 2))
        
        check_in = {
            "check_in_id": chk_id,
            "employee_id": target_goal["employee_id"],
            "goal_id": target_goal["goal_id"],
            "review_cycle_id": cycle_id,
            "check_in_date": chk_date,
            "progress_update": progress_snapshot,
            "employee_comments": f"Sprint milestone update: Progress reported at {progress_snapshot}%. Work progressing on track.",
            "manager_comments": "Good momentum. Continue focusing on milestone deliverables." if emp["manager_id"] else None,
            "blockers": "None" if c_idx % 4 != 0 else "Waiting for cross-team PR review and deployment window.",
            "next_steps": "Finalize integration tests and merge staging release."
        }
        check_ins.append(check_in)
        
        # Link an evidence record for every 2nd check-in
        if c_idx % 2 == 0:
            evd_id = f"EVD-{len(evidences)+1:06d}"
            ev_type = evidence_types[c_idx % len(evidence_types)]
            ev_url = f"https://artifacts.yottaperf.internal/{ev_type.lower()}/{target_goal['goal_id']}/{c_idx}"
            
            evd = {
                "evidence_id": evd_id,
                "check_in_id": chk_id,
                "evidence_type": ev_type,
                "reference_url": ev_url,
                "description": f"Verified supporting evidence for {target_goal['title']} checkpoint.",
                "uploaded_by": target_goal["employee_id"],
                "uploaded_date": chk_date,
                "verification_status": "VERIFIED"
            }
            evidences.append(evd)

    return check_ins, evidences


def generate_feedback_and_reviews(
    config: GeneratorConfig,
    employees: List[Dict[str, Any]],
    competencies: List[Dict[str, Any]],
    review_cycles: List[Dict[str, Any]],
    goals: List[Dict[str, Any]],
    evidences: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Feedbacks (Self, Manager, Peer), FeedbackEvidence bridges,
    ReviewPermissions, and Reviews with derived scores.
    """
    feedbacks = []
    feedback_evidences = []
    review_permissions = []
    reviews = []

    # Map department peers
    dept_peers: Dict[str, List[str]] = {}
    emp_map = {e["employee_id"]: e for e in employees}
    for e in employees:
        dept = e["department"]
        dept_peers.setdefault(dept, []).append(e["employee_id"])

    # Pre-index goals by (employee_id, cycle_id)
    emp_goals: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for g in goals:
        key = (g["employee_id"], g["review_cycle_id"])
        emp_goals.setdefault(key, []).append(g)

    fb_counter = 1
    perm_counter = 1
    rev_counter = 1

    for cycle in review_cycles:
        cycle_id = cycle["cycle_id"]
        is_closed = (cycle["stage"] == "CLOSED")
        
        for emp in employees:
            emp_id = emp["employee_id"]
            mgr_id = emp["manager_id"]
            dept = emp["department"]

            emp_num = int(emp_id.split("-")[1])
            # 1. Self Feedback on 2 competencies
            comp1 = competencies[emp_num % len(competencies)]
            comp2 = competencies[(emp_num + 1) % len(competencies)]
            
            self_rating_1 = round(3.5 + (1.2 * rng.random()), 2)
            self_rating_1 = min(5.0, max(1.0, self_rating_1))
            fb_self = {
                "feedback_id": f"FB-{fb_counter:06d}",
                "subject_employee_id": emp_id,
                "reviewer_employee_id": emp_id,
                "review_cycle_id": cycle_id,
                "feedback_type": "SELF",
                "competency_id": comp1["competency_id"],
                "rating": self_rating_1,
                "comments": f"Self assessment on {comp1['name']}: Consistently met delivery targets and demonstrated technical diligence.",
                "submission_date": cycle["submission_deadline"],
                "status": "SUBMITTED"
            }
            feedbacks.append(fb_self)
            fb_counter += 1

            # 2. Manager Feedback (if manager exists)
            mgr_rating = self_rating_1
            if mgr_id and mgr_id in emp_map:
                mgr_rating = round(3.0 + (1.8 * rng.random()), 2)
                mgr_rating = min(5.0, max(1.0, mgr_rating))
                fb_mgr = {
                    "feedback_id": f"FB-{fb_counter:06d}",
                    "subject_employee_id": emp_id,
                    "reviewer_employee_id": mgr_id,
                    "review_cycle_id": cycle_id,
                    "feedback_type": "MANAGER",
                    "competency_id": comp1["competency_id"],
                    "rating": mgr_rating,
                    "comments": f"Manager evaluation on {comp1['name']}: Reliable delivery, strong engineering ownership.",
                    "submission_date": cycle["submission_deadline"],
                    "status": "SUBMITTED"
                }
                feedbacks.append(fb_mgr)
                fb_counter += 1

            # 3. Peer Feedback from same department
            peers = [p for p in dept_peers.get(dept, []) if p != emp_id]
            peer_rating = self_rating_1
            if peers:
                cycle_offset = 1 if "2025" in cycle_id else 2
                peer_id = peers[(emp_num + cycle_offset) % len(peers)]
                peer_rating = round(3.2 + (1.5 * rng.random()), 2)
                peer_rating = min(5.0, max(1.0, peer_rating))
                
                # Register review permission bridge
                perm_record = {
                    "permission_id": f"RP-{perm_counter:06d}",
                    "review_cycle_id": cycle_id,
                    "subject_employee_id": emp_id,
                    "reviewer_employee_id": peer_id,
                    "relationship_type": "PEER",
                    "granted_by": mgr_id or emp_id,
                }
                review_permissions.append(perm_record)
                perm_counter += 1

                fb_peer = {
                    "feedback_id": f"FB-{fb_counter:06d}",
                    "subject_employee_id": emp_id,
                    "reviewer_employee_id": peer_id,
                    "review_cycle_id": cycle_id,
                    "feedback_type": "PEER",
                    "competency_id": comp2["competency_id"],
                    "rating": peer_rating,
                    "comments": f"Peer feedback on {comp2['name']}: Great partner to work with, responsive during sprint planning.",
                    "submission_date": cycle["submission_deadline"],
                    "status": "SUBMITTED"
                }
                feedbacks.append(fb_peer)
                
                # Attach evidence link to peer feedback if evidence exists
                if evidences:
                    matching_ev = evidences[(fb_counter - 1) % len(evidences)]
                    feedback_evidences.append({
                        "feedback_id": fb_peer["feedback_id"],
                        "evidence_id": matching_ev["evidence_id"]
                    })
                fb_counter += 1

            # 4. Synthesize Formal Performance Review
            # Calculate Goal Score (50%)
            g_list = emp_goals.get((emp_id, cycle_id), [])
            if g_list:
                goal_score = round(sum(float(g["calculated_progress"]) for g in g_list) / len(g_list), 2)
            else:
                goal_score = 75.00  # Baseline average
            
            # Calculate Competency Score (30%) & Feedback Score (20%)
            # Mapped to 0-100 scale: (rating / 5.0) * 100
            comp_score = round(((self_rating_1 + mgr_rating) / (2 * 5.0)) * 100.0, 2)
            fb_score = round((peer_rating / 5.0) * 100.0, 2)

            # Final Reconciled Score
            w_goal = float(cycle["goal_weight"]) / 100.0
            w_comp = float(cycle["competency_weight"]) / 100.0
            w_fb = float(cycle["feedback_weight"]) / 100.0
            final_score = round((goal_score * w_goal) + (comp_score * w_comp) + (fb_score * w_fb), 2)

            if final_score >= 90.0:
                rating_cat = "OUTSTANDING"
            elif final_score >= 75.0:
                rating_cat = "EXCEEDS_EXPECTATIONS"
            elif final_score >= 60.0:
                rating_cat = "MEETS_EXPECTATIONS"
            else:
                rating_cat = "NEEDS_IMPROVEMENT"

            stage = "COMPLETED" if is_closed else ("APPROVED" if final_score >= 80 else "MANAGER_REVIEW_PENDING")
            
            review_rec = {
                "review_id": f"REV-2026-{rev_counter:06d}",
                "employee_id": emp_id,
                "review_cycle_id": cycle_id,
                "goal_score": goal_score,
                "competency_score": comp_score,
                "feedback_score": fb_score,
                "final_score": final_score,
                "rating_category": rating_cat,
                "stage": stage,
                "self_comments": "Met core strategic objectives and supported team roadmap.",
                "manager_comments": "Solid execution throughout the cycle. Well-calibrated results.",
                "hr_comments": "Calibrated with department distribution benchmarks." if is_closed else None,
            }
            reviews.append(review_rec)
            rev_counter += 1

    return feedbacks, feedback_evidences, review_permissions, reviews


def generate_development_plans(
    config: GeneratorConfig,
    employees: List[Dict[str, Any]],
    competencies: List[Dict[str, Any]],
    reviews: List[Dict[str, Any]],
    rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Identifies capability gaps and generates development plans, activities, and approvals.
    """
    development_plans = []
    development_activities = []
    plan_approvals = []

    plan_counter = 1
    act_counter = 1
    appr_counter = 1

    review_map = {r["employee_id"]: r for r in reviews}

    # Generate development plans for approximately 30% of employees
    for idx, emp in enumerate(employees):
        if idx % 3 == 0:
            emp_id = emp["employee_id"]
            plan_id = f"DP-{plan_counter:06d}"
            comp = competencies[idx % len(competencies)]
            rev = review_map.get(emp_id)
            rev_id = rev["review_id"] if rev else None

            plan = {
                "plan_id": plan_id,
                "employee_id": emp_id,
                "review_id": rev_id,
                "competency_id": comp["competency_id"],
                "current_level": "Proficient",
                "target_level": "Advanced / Subject Matter Expert",
                "recommended_action": f"Deepen expertise in {comp['name']} through targeted architecture exercises and hands-on system designs.",
                "learning_resources": "Internal Engineering Academy, O'Reilly Learning Path, Cloud Architecture Masterclass",
                "start_date": "2026-02-01",
                "target_completion_date": "2026-08-31",
                "status": "IN_PROGRESS",
                "approval_status": "APPROVED"
            }
            development_plans.append(plan)

            # Generate 2 development activities
            act1 = {
                "activity_id": f"DA-{act_counter:06d}",
                "plan_id": plan_id,
                "title": f"Complete {comp['name']} Intensive Course",
                "activity_type": "COURSE",
                "resource_url": "https://learning.yottaperf.internal/courses/arch-301",
                "status": "COMPLETED",
                "completed_date": "2026-04-15"
            }
            act2 = {
                "activity_id": f"DA-{act_counter+1:06d}",
                "plan_id": plan_id,
                "title": f"Lead Design Review on {comp['name']} for Team",
                "activity_type": "PROJECT",
                "resource_url": "https://wiki.yottaperf.internal/rfc/402",
                "status": "IN_PROGRESS",
                "completed_date": None
            }
            development_activities.extend([act1, act2])
            act_counter += 2

            # Manager Approval
            if emp["manager_id"]:
                plan_approvals.append({
                    "approval_id": f"DPA-{appr_counter:06d}",
                    "plan_id": plan_id,
                    "approver_id": emp["manager_id"],
                    "approval_role": "MANAGER",
                    "decision": "APPROVED",
                    "comments": "Approved. Strong alignment with department growth targets."
                })
                appr_counter += 1

            plan_counter += 1

    return development_plans, development_activities, plan_approvals
