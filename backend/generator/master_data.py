from datetime import date, datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
import random
from faker import Faker
from backend.generator.config import GeneratorConfig
from backend.app.core.security import get_password_hash


def generate_roles() -> List[Dict[str, Any]]:
    return [
        {"role_id": "ROLE-EMP", "name": "EMPLOYEE", "description": "Standard employee access: own goals, check-ins, self-review"},
        {"role_id": "ROLE-MGR", "name": "MANAGER", "description": "Managerial access: direct reports, approvals, team reviews"},
        {"role_id": "ROLE-HR", "name": "HR_PARTNER", "description": "HR partner: cycle management, calibration, organizational oversight"},
        {"role_id": "ROLE-OPS", "name": "IT_OPS", "description": "Operations & IT: synthetic generation, validation, system monitoring"},
        {"role_id": "ROLE-ADM", "name": "ADMIN", "description": "System administrator: full configuration and security administration"},
    ]


def generate_competencies(config: GeneratorConfig) -> List[Dict[str, Any]]:
    catalog = [
        ("COMP-TECH-01", "Technical Skills", "Software Architecture & System Design", "Demonstrates sound architectural choices and maintainable system boundaries."),
        ("COMP-TECH-02", "Technical Skills", "Code Quality & Automated Testing", "Writes clean, readable, high-coverage code adhering to engineering standards."),
        ("COMP-TECH-03", "Technical Skills", "Cloud Infrastructure & Scalability", "Designs scalable, fault-tolerant cloud systems."),
        ("COMP-COMM-01", "Communication", "Cross-Functional Collaboration", "Articulates complex ideas clearly across disciplines."),
        ("COMP-COMM-02", "Communication", "Technical Documentation & Mentorship", "Produces thorough design docs and mentors team members."),
        ("COMP-PROB-01", "Problem Solving", "Root Cause Analysis & Debugging", "Diagnoses complex bugs and incidents methodically."),
        ("COMP-LEAD-01", "Leadership", "Strategic Alignment & Execution", "Translates company vision into measurable roadmaps."),
        ("COMP-LEAD-02", "Leadership", "Team Empowerment & Coaching", "Guides direct reports and cultivates engineering growth."),
        ("COMP-COLL-01", "Collaboration", "Partner Engagement & Empathy", "Fosters an inclusive, high-trust engineering culture."),
        ("COMP-ADAP-01", "Adaptability", "Agile Execution & Change Navigation", "Pivots effectively amidst ambiguous business requirements."),
        ("COMP-OWNR-01", "Ownership", "End-to-End Delivery & Accountability", "Owns outcomes from ideation through production support."),
        ("COMP-TIME-01", "Time Management", "Priority & Milestone Delivery", "Consistently hits sprint and quarterly delivery milestones.")
    ]
    selected = catalog[:config.num_competencies]
    competencies = []
    for c_id, category, name, desc in selected:
        competencies.append({
            "competency_id": c_id,
            "category": category,
            "name": name,
            "description": desc,
            "is_active": True
        })
    return competencies


def generate_review_cycles() -> List[Dict[str, Any]]:
    return [
        {
            "cycle_id": "CYCLE-2025-H2",
            "cycle_name": "2025 H2 Performance Review Cycle",
            "start_date": "2025-07-01",
            "end_date": "2025-12-31",
            "submission_deadline": "2025-12-15",
            "stage": "CLOSED",
            "goal_weight": 50.00,
            "competency_weight": 30.00,
            "feedback_weight": 20.00,
        },
        {
            "cycle_id": "CYCLE-2026-H1",
            "cycle_name": "2026 H1 Performance Review Cycle",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "submission_deadline": "2026-06-15",
            "stage": "OPEN",
            "goal_weight": 50.00,
            "competency_weight": 30.00,
            "feedback_weight": 20.00,
        }
    ]


def generate_organization(
    config: GeneratorConfig, fake: Faker, rng: random.Random
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generates Employees, UserAccounts, EmployeeRoles, Managers, and Initial Manager Histories.
    Hierarchy is strictly hierarchical DAG (tree structure) ensuring zero cycles in baseline.
    """
    departments = [
        "Engineering", "Product", "Sales", "Marketing",
        "Customer Success", "Human Resources", "Operations", "Finance"
    ]
    
    # Fixed deterministic bcrypt hash for 'YottaPerf2026!' ensuring bit-for-bit reproducibility
    default_hashed_pwd = "$2b$12$1M31V5N4r5bTFFj4rEsPY..QvRBdKaqQ0WfgPX0GUK0H0S.JrIKC6"

    employees = []
    user_accounts = []
    employee_roles = []
    managers = []
    manager_histories = []

    # Level structure:
    # 0: CEO (EMP-000001)
    # 1: VPs / Executives (e.g. 5-8 executives)
    # 2: Directors (e.g. 15-30 directors)
    # 3: Team Leads / Managers (e.g. remaining up to config.num_managers)
    # 4: ICs (Individual Contributors)

    num_emps = config.num_employees
    num_mgrs = min(config.num_managers, num_emps - 1)

    # 1. Create CEO
    ceo_id = "EMP-000001"
    ceo = {
        "employee_id": ceo_id,
        "first_name": "Eleanor",
        "last_name": "Vance",
        "email": "eleanor.vance@yottaperf.internal",
        "department": "Executive",
        "job_title": "Chief Executive Officer",
        "job_level": "EXEC",
        "manager_id": None,
        "is_active": True,
        "hire_date": "2020-01-15",
    }
    employees.append(ceo)
    user_accounts.append({
        "user_id": "USR-000001",
        "employee_id": ceo_id,
        "username": "eleanor.vance",
        "email": ceo["email"],
        "hashed_password": default_hashed_pwd,
        "is_active": True
    })
    employee_roles.append({"employee_id": ceo_id, "role_id": "ROLE-ADM"})
    employee_roles.append({"employee_id": ceo_id, "role_id": "ROLE-MGR"})
    managers.append({
        "manager_id": "MGR-000001",
        "employee_id": ceo_id,
        "management_level": "Executive",
        "budget_authority": 5000000.00
    })

    # Divide managers into VP, Director, and Manager tiers
    vp_count = min(7, max(2, num_mgrs // 10))
    dir_count = min(25, max(4, num_mgrs // 3))
    lead_count = num_mgrs - 1 - vp_count - dir_count
    if lead_count < 0:
        lead_count = 0
        dir_count = max(0, num_mgrs - 1 - vp_count)

    mgr_index = 2
    vp_ids = []
    dir_ids = []
    lead_ids = []

    # Generate VPs (report to CEO)
    for i in range(vp_count):
        emp_id = f"EMP-{mgr_index:06d}"
        mgr_profile_id = f"MGR-{mgr_index:06d}"
        dept = departments[i % len(departments)]
        fn = fake.first_name()
        ln = fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{mgr_index}@yottaperf.internal"
        
        emp = {
            "employee_id": emp_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "department": dept,
            "job_title": f"Vice President of {dept}",
            "job_level": "EXEC",
            "manager_id": ceo_id,
            "is_active": True,
            "hire_date": "2020-03-01",
        }
        employees.append(emp)
        vp_ids.append(emp_id)
        user_accounts.append({
            "user_id": f"USR-{mgr_index:06d}",
            "employee_id": emp_id,
            "username": f"{fn.lower()}.{ln.lower()}",
            "email": email,
            "hashed_password": default_hashed_pwd,
            "is_active": True
        })
        employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-MGR"})
        if dept == "Human Resources":
            employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-HR"})
        managers.append({
            "manager_id": mgr_profile_id,
            "employee_id": emp_id,
            "management_level": "VP",
            "budget_authority": 1000000.00
        })
        manager_histories.append({
            "history_id": f"EMH-{len(manager_histories)+1:06d}",
            "employee_id": emp_id,
            "manager_id": ceo_id,
            "effective_start_date": "2020-03-01",
            "effective_end_date": None,
            "transfer_reason": "Initial VP Appointment"
        })
        mgr_index += 1

    # Generate Directors (report to VPs)
    for i in range(dir_count):
        emp_id = f"EMP-{mgr_index:06d}"
        mgr_profile_id = f"MGR-{mgr_index:06d}"
        parent_vp = vp_ids[i % len(vp_ids)]
        dept = next(e["department"] for e in employees if e["employee_id"] == parent_vp)
        fn = fake.first_name()
        ln = fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{mgr_index}@yottaperf.internal"
        
        emp = {
            "employee_id": emp_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "department": dept,
            "job_title": f"Director of {dept}",
            "job_level": "M4",
            "manager_id": parent_vp,
            "is_active": True,
            "hire_date": "2021-01-15",
        }
        employees.append(emp)
        dir_ids.append(emp_id)
        user_accounts.append({
            "user_id": f"USR-{mgr_index:06d}",
            "employee_id": emp_id,
            "username": f"{fn.lower()}.{ln.lower()}",
            "email": email,
            "hashed_password": default_hashed_pwd,
            "is_active": True
        })
        employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-MGR"})
        if dept == "Human Resources":
            employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-HR"})
        managers.append({
            "manager_id": mgr_profile_id,
            "employee_id": emp_id,
            "management_level": "Director",
            "budget_authority": 300000.00
        })
        manager_histories.append({
            "history_id": f"EMH-{len(manager_histories)+1:06d}",
            "employee_id": emp_id,
            "manager_id": parent_vp,
            "effective_start_date": "2021-01-15",
            "effective_end_date": None,
            "transfer_reason": "Director Promotion"
        })
        mgr_index += 1

    # Generate Managers / Leads (report to Directors)
    for i in range(lead_count):
        emp_id = f"EMP-{mgr_index:06d}"
        mgr_profile_id = f"MGR-{mgr_index:06d}"
        parent_dir = dir_ids[i % len(dir_ids)] if dir_ids else vp_ids[0]
        dept = next(e["department"] for e in employees if e["employee_id"] == parent_dir)
        fn = fake.first_name()
        ln = fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{mgr_index}@yottaperf.internal"
        
        emp = {
            "employee_id": emp_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "department": dept,
            "job_title": f"Engineering Lead" if dept == "Engineering" else f"{dept} Manager",
            "job_level": "M2",
            "manager_id": parent_dir,
            "is_active": True,
            "hire_date": "2022-04-10",
        }
        employees.append(emp)
        lead_ids.append(emp_id)
        user_accounts.append({
            "user_id": f"USR-{mgr_index:06d}",
            "employee_id": emp_id,
            "username": f"{fn.lower()}.{ln.lower()}",
            "email": email,
            "hashed_password": default_hashed_pwd,
            "is_active": True
        })
        employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-MGR"})
        managers.append({
            "manager_id": mgr_profile_id,
            "employee_id": emp_id,
            "management_level": "Team Lead",
            "budget_authority": 50000.00
        })
        manager_histories.append({
            "history_id": f"EMH-{len(manager_histories)+1:06d}",
            "employee_id": emp_id,
            "manager_id": parent_dir,
            "effective_start_date": "2022-04-10",
            "effective_end_date": None,
            "transfer_reason": "Team Lead Assignment"
        })
        mgr_index += 1

    # Eligible managers pool for remaining ICs: lead_ids or dir_ids
    active_managers_pool = lead_ids if lead_ids else (dir_ids if dir_ids else vp_ids)

    # Generate Individual Contributors (ICs)
    ic_titles = {
        "Engineering": ["Software Engineer", "Senior Software Engineer", "DevOps Engineer", "QA Automation Engineer", "Staff Engineer"],
        "Product": ["Product Manager", "Associate Product Manager", "Product Designer", "Data Analyst"],
        "Sales": ["Account Executive", "Sales Development Rep", "Enterprise Sales Specialist"],
        "Marketing": ["Content Strategist", "Growth Marketer", "SEO Specialist"],
        "Customer Success": ["Customer Success Specialist", "Technical Support Engineer"],
        "Human Resources": ["People Operations Partner", "Technical Recruiter", "HR Generalist"],
        "Operations": ["IT Systems Administrator", "Cloud Operations Specialist"],
        "Finance": ["Financial Analyst", "Staff Accountant"]
    }
    levels = ["IC1", "IC2", "IC3", "IC4", "IC5"]

    for idx in range(mgr_index, num_emps + 1):
        emp_id = f"EMP-{idx:06d}"
        mgr_emp_id = active_managers_pool[(idx - mgr_index) % len(active_managers_pool)]
        mgr_dept = next(e["department"] for e in employees if e["employee_id"] == mgr_emp_id)
        
        dept_titles = ic_titles.get(mgr_dept, ["Specialist", "Analyst"])
        title = dept_titles[idx % len(dept_titles)]
        level = levels[idx % len(levels)]
        fn = fake.first_name()
        ln = fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{idx}@yottaperf.internal"
        
        hire_day = 1 + (idx % 25)
        hire_month = 1 + (idx % 12)
        hire_year = 2023 + (idx % 3)
        hire_date_str = f"{hire_year}-{hire_month:02d}-{hire_day:02d}"

        emp = {
            "employee_id": emp_id,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "department": mgr_dept,
            "job_title": title,
            "job_level": level,
            "manager_id": mgr_emp_id,
            "is_active": True,
            "hire_date": hire_date_str,
        }
        employees.append(emp)
        user_accounts.append({
            "user_id": f"USR-{idx:06d}",
            "employee_id": emp_id,
            "username": f"{fn.lower()}.{ln.lower()}{idx}",
            "email": email,
            "hashed_password": default_hashed_pwd,
            "is_active": True
        })
        
        # Assign role
        employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-EMP"})
        if "IT Systems" in title or "DevOps" in title:
            employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-OPS"})
        elif mgr_dept == "Human Resources":
            employee_roles.append({"employee_id": emp_id, "role_id": "ROLE-HR"})

        manager_histories.append({
            "history_id": f"EMH-{len(manager_histories)+1:06d}",
            "employee_id": emp_id,
            "manager_id": mgr_emp_id,
            "effective_start_date": hire_date_str,
            "effective_end_date": None,
            "transfer_reason": "Initial Hire Placement"
        })

    return employees, user_accounts, employee_roles, managers, manager_histories
