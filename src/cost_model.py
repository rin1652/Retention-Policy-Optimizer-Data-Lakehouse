"""Linear extra-history cost and explicit policy feasibility (TASK-04)."""
import argparse
import json
from pathlib import Path

from src.config import finite_number, load_config, validate_cost_config


def history_cost_gb(ttl_days, profiles):
    """Compute sum(history_gb_per_day * TTL); current data is excluded."""
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("profiles must be nonempty")
    if not isinstance(ttl_days, dict):
        raise ValueError("ttl_days must be a table_id mapping")
    ids = {p["table_id"] for p in profiles}
    if len(ids) != len(profiles):
        raise ValueError("duplicate profile table_id")
    if set(ttl_days) != ids:
        raise ValueError("TTL mapping must contain exactly every configured profile")
    costs = []
    for profile in profiles:
        ttl = finite_number(ttl_days[profile["table_id"]], "TTL")
        rate = finite_number(profile["history_gb_per_day"], "history rate", positive=True)
        costs.append(finite_number(rate * ttl, "history cost"))
    return finite_number(sum(costs), "total history cost")


def minimum_required_cost_gb(config, *, on_grid=False):
    validate_cost_config(config)
    ttl = {}
    for profile in config["profiles"]:
        minimum = profile["min_ttl_days"]
        if on_grid:
            candidates = [t for t in config["ttl_grid_days"] if t >= minimum]
            if not candidates:
                return None
            minimum = min(candidates)
        ttl[profile["table_id"]] = minimum
    return history_cost_gb(ttl, config["profiles"])


def check_policy(ttl_days, config, budget_gb=None):
    """Return invalid status/reasons instead of claiming coverage for a bad policy.

    Malformed config/budget raises ValueError; bad TTL input is an invalid policy.
    Grid membership is part of feasibility for contract v1.0.
    """
    validate_cost_config(config)
    budget = config["budget"]["main_gb"] if budget_gb is None else budget_gb
    finite_number(budget, "budget_gb")
    violations = []
    try:
        cost = history_cost_gb(ttl_days, config["profiles"])
    except (ValueError, OverflowError) as error:
        cost = None
        violations.append({"code": "invalid_ttl_mapping", "message": str(error)})
    if cost is not None:
        for profile in config["profiles"]:
            table = profile["table_id"]
            if ttl_days[table] < profile["min_ttl_days"]:
                violations.append({"code": "min_ttl_violation", "table_id": table})
            if ttl_days[table] not in config["ttl_grid_days"]:
                violations.append({"code": "ttl_grid_violation", "table_id": table})
        if cost > budget:
            violations.append({"code": "budget_violation"})
    minimum = minimum_required_cost_gb(config)
    grid_minimum = minimum_required_cost_gb(config, on_grid=True)
    return {
        "status": "valid" if not violations else "invalid",
        "feasible": not violations, "coverage_claim_allowed": not violations,
        "budget_gb": budget, "cost_gb": cost,
        "remaining_budget_gb": None if cost is None else budget - cost,
        "minimum_cost_gb": minimum, "minimum_grid_cost_gb": grid_minimum,
        "any_grid_policy_feasible": grid_minimum is not None and grid_minimum <= budget,
        "cost_kind": "extra_history_overhead", "violations": violations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiment.sample.json")
    parser.add_argument("--policy", help="JSON TTL mapping or policy with ttl_days")
    parser.add_argument("--budget", type=float)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.policy:
            value = json.loads(Path(args.policy).read_text(encoding="utf-8-sig"))
            ttl = value.get("ttl_days", value) if isinstance(value, dict) else value
        else:
            ttl = {p["table_id"]: p["min_ttl_days"] for p in config["profiles"]}
        result = check_policy(ttl, config, args.budget)
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        parser.exit(2, f"Cost validation failed: {error}\n")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    if not result["feasible"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
