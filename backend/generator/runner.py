import os
import sys
import argparse
import random
from typing import Dict, List, Any, Tuple
from faker import Faker
import numpy as np

from backend.generator.config import get_generator_config, GeneratorConfig
from backend.generator.master_data import (
    generate_roles, generate_competencies, generate_review_cycles, generate_organization
)
from backend.generator.transactions import (
    generate_goals_and_key_results, generate_check_ins_and_evidences,
    generate_feedback_and_reviews, generate_development_plans
)
from backend.generator.events import generate_event_histories
from backend.generator.anomalies import inject_anomalies
from backend.generator.ground_truth import export_ground_truth
from backend.generator.exporter import export_dataset


def generate_all_data(config: GeneratorConfig) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
    """
    Orchestrates deterministic dataset generation:
    1. Parent master data first (Roles, Competencies, Cycles, Employees, Accounts, Managers)
    2. Child business transactions (Goals, Key Results, Check-Ins, Evidences, Feedbacks, Reviews, Plans)
    3. Event histories (GoalHistory, ReviewHistory, AuditEvents)
    4. Deliberate anomaly injection + separate ground truth
    """
    # Seed all pseudo-random number generators
    random.seed(config.seed)
    np.random.seed(config.seed)
    fake = Faker()
    fake.seed_instance(config.seed)
    rng = random.Random(config.seed)

    # 1. Master Data
    roles = generate_roles()
    competencies = generate_competencies(config)
    review_cycles = generate_review_cycles()
    employees, user_accounts, employee_roles, managers, manager_histories = generate_organization(
        config, fake, rng
    )

    # 2. Transactions
    goals, key_results = generate_goals_and_key_results(config, employees, review_cycles, rng)
    check_ins, evidences = generate_check_ins_and_evidences(config, goals, employees, rng)
    feedbacks, feedback_evidences, review_permissions, reviews = generate_feedback_and_reviews(
        config, employees, competencies, review_cycles, goals, evidences, rng
    )
    dev_plans, dev_activities, plan_approvals = generate_development_plans(
        config, employees, competencies, reviews, rng
    )

    # 3. Events & Histories
    goal_histories, review_histories, audit_events = generate_event_histories(goals, reviews, employees)

    # 4. Injected Anomalies & Ground Truth
    anomalies, ground_truth_records = inject_anomalies(
        config, employees, goals, key_results, feedbacks, competencies, review_cycles
    )

    tables_data = {
        "roles": roles,
        "competencies": competencies,
        "review_cycles": review_cycles,
        "employees": employees,
        "user_accounts": user_accounts,
        "employee_roles": employee_roles,
        "managers": managers,
        "employee_manager_histories": manager_histories,
        "goals": goals,
        "key_results": key_results,
        "goal_histories": goal_histories,
        "check_ins": check_ins,
        "evidences": evidences,
        "feedbacks": feedbacks,
        "feedback_evidence": feedback_evidences,
        "review_permissions": review_permissions,
        "reviews": reviews,
        "review_histories": review_histories,
        "development_plans": dev_plans,
        "development_activities": dev_activities,
        "development_plan_approvals": plan_approvals,
        "anomalies": anomalies,
        "audit_events": audit_events,
    }

    return tables_data, ground_truth_records


def insert_into_database(tables_data: Dict[str, List[Dict[str, Any]]]):
    """
    Inserts generated dictionaries directly into the active database session.
    """
    from backend.app.core.database import SessionLocal, engine, Base
    from backend.app.models import (
        Role, Competency, ReviewCycle, Employee, UserAccount, EmployeeRole,
        Manager, EmployeeManagerHistory, Goal, KeyResult, GoalHistory,
        CheckIn, Evidence, Feedback, FeedbackEvidence, ReviewPermission,
        Review, ReviewHistory, DevelopmentPlan, DevelopmentActivity,
        DevelopmentPlanApproval, Anomaly, AuditEvent
    )
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        model_map = {
            "roles": Role,
            "competencies": Competency,
            "review_cycles": ReviewCycle,
            "employees": Employee,
            "user_accounts": UserAccount,
            "employee_roles": EmployeeRole,
            "managers": Manager,
            "employee_manager_histories": EmployeeManagerHistory,
            "goals": Goal,
            "key_results": KeyResult,
            "goal_histories": GoalHistory,
            "check_ins": CheckIn,
            "evidences": Evidence,
            "feedbacks": Feedback,
            "feedback_evidence": FeedbackEvidence,
            "review_permissions": ReviewPermission,
            "reviews": Review,
            "review_histories": ReviewHistory,
            "development_plans": DevelopmentPlan,
            "development_activities": DevelopmentActivity,
            "development_plan_approvals": DevelopmentPlanApproval,
            "anomalies": Anomaly,
            "audit_events": AuditEvent,
        }

        for table_name, model_cls in model_map.items():
            records = tables_data.get(table_name, [])
            if not records:
                continue
            for r in records:
                obj = model_cls(**r)
                db.merge(obj)
            db.commit()
            print(f"Loaded {len(records)} records into {table_name}")
    except Exception as e:
        db.rollback()
        print(f"Error during database insertion: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="YottaPerf Deterministic Synthetic Data Generator")
    parser.add_argument("--mode", choices=["starter", "full"], default="starter", help="Generation mode (starter or full)")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed (default: 20261022)")
    parser.add_argument("--output-dir", type=str, default=None, help="Target export directory")
    parser.add_argument("--insert-db", action="store_true", help="Insert records into active database")
    
    args = parser.parse_args()

    config = get_generator_config(mode=args.mode, seed=args.seed)
    
    if args.output_dir:
        target_dir = args.output_dir
    else:
        target_dir = os.path.join("generated_data", args.mode)

    print(f"=== Starting YottaPerf Data Generator ===")
    print(f"Mode: {config.mode} | Seed: {config.seed} | Target Output: {target_dir}")
    print(f"Targets: {config.num_employees} Employees, {config.num_managers} Managers, {config.num_goals} Goals, {config.num_checkins} Check-ins")

    tables_data, ground_truth_records = generate_all_data(config)

    # Export dataset (CSV, JSON, SQL seed, Manifest)
    manifest = export_dataset(tables_data, target_dir, config.mode, config.seed)
    
    # Export ground truth dataset strictly separated
    export_ground_truth(ground_truth_records, target_dir)

    print(f"Data generation complete!")
    print(f"Generated entities:")
    for k, v in manifest["entity_row_counts"].items():
        print(f"  - {k}: {v}")
    print(f"Dataset SHA-256 Checksum: {manifest['dataset_checksum']}")
    print(f"Manifest written to: {os.path.join(target_dir, 'manifest.json')}")
    print(f"Ground truth written to: {os.path.join(target_dir, 'ground_truth.csv')}")

    if args.insert_db:
        print("\nLoading dataset into database...")
        insert_into_database(tables_data)
        print("Database load completed.")


if __name__ == "__main__":
    main()
