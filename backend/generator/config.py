from dataclasses import dataclass
from datetime import date
from typing import Dict, Any


@dataclass(frozen=True)
class GeneratorConfig:
    mode: str
    seed: int
    reference_date: date
    num_employees: int
    num_managers: int
    num_goals: int
    num_checkins: int
    num_cycles: int
    num_competencies: int
    anomalies_per_type: int


def get_generator_config(mode: str = "starter", seed: int = 20261022) -> GeneratorConfig:
    ref_date = date(2026, 6, 30)
    
    if mode == "full":
        return GeneratorConfig(
            mode="full",
            seed=seed,
            reference_date=ref_date,
            num_employees=3000,
            num_managers=500,
            num_goals=10000,
            num_checkins=20000,
            num_cycles=2,
            num_competencies=12,
            anomalies_per_type=20,
        )
    else:  # starter
        return GeneratorConfig(
            mode="starter",
            seed=seed,
            reference_date=ref_date,
            num_employees=150,
            num_managers=25,
            num_goals=500,
            num_checkins=1200,
            num_cycles=2,
            num_competencies=10,
            anomalies_per_type=5,
        )
