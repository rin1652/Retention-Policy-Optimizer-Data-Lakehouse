import itertools
import json
from datetime import datetime, timedelta, timezone

from src.cost_model import check_policy

VIETNAM = timezone(timedelta(hours=7))

def get_baseline_policy(config, budget_gb=None, training_scenario=None, seed=None):
    from src.policies import uniform_baseline
    return uniform_baseline(
        config, budget_gb,
        training_scenario=training_scenario, development_seed=seed,
    )

def compute_cost(ttl_vector: dict, config: dict) -> float:
    profiles = config.get("profiles", [])
    return sum(p["history_gb_per_day"] * ttl_vector.get(p["table_id"], 0) for p in profiles)

def optimize_policy(config: dict, incidents: list, budget_gb: float, training_scenario: str, seed: int) -> dict:
    from src.evaluate import evaluate_policy
    
    grid = config.get("ttl_grid_days", [])
    profiles = config.get("profiles", [])
    table_ids = [p["table_id"] for p in profiles]
    
    best_policy = None
    best_coverage = -1.0
    best_cost = float('inf')
    best_vector_tuple = None
    
    for ttl_tuple in itertools.product(grid, repeat=len(profiles)):
        ttl_days = {table_ids[i]: ttl_tuple[i] for i in range(len(profiles))}
        
        min_ttl_ok = all(ttl_days[p["table_id"]] >= p["min_ttl_days"] for p in profiles)
        if not min_ttl_ok:
            continue
            
        cost = compute_cost(ttl_days, config)
        if cost > budget_gb:
            continue
            
        candidate = {
            "ttl_days": ttl_days,
            "budget_gb": budget_gb,
            "feasible": True
        }
        
        res = evaluate_policy(config, candidate, incidents)
        coverage = res["metrics"]["coverage_total"]
        
        if coverage > best_coverage:
            best_coverage = coverage
            best_cost = cost
            best_vector_tuple = ttl_tuple
            best_policy = candidate
        elif abs(coverage - best_coverage) < 1e-9:
            if cost < best_cost:
                best_coverage = coverage
                best_cost = cost
                best_vector_tuple = ttl_tuple
                best_policy = candidate
            elif abs(cost - best_cost) < 1e-9:
                if best_vector_tuple is None or ttl_tuple < best_vector_tuple:
                    best_coverage = coverage
                    best_cost = cost
                    best_vector_tuple = ttl_tuple
                    best_policy = candidate
                    
    if not best_policy:
        return {
            "policy_id": f"optimized-{training_scenario}-dev{seed}-B{budget_gb}",
            "kind": "optimized_per_profile",
            "ttl_days": {tid: grid[0] for tid in table_ids},
            "budget_gb": budget_gb,
            "cost_gb": compute_cost({tid: grid[0] for tid in table_ids}, config),
            "feasible": False,
            "training_scenario": training_scenario,
            "development_seed": seed,
            "locked_on_split": "development"
        }
        
    best_policy["policy_id"] = f"optimized-{training_scenario}-dev{seed}-B{budget_gb}"
    best_policy["kind"] = "optimized_per_profile"
    best_policy["cost_gb"] = best_cost
    best_policy["training_scenario"] = training_scenario
    best_policy["development_seed"] = seed
    best_policy["locked_on_split"] = "development"
    return best_policy
