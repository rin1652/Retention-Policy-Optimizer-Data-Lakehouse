"""Uniform TTL baseline chosen from config alone, without holdout (TASK-06)."""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.config import config_hash, finite_number, load_config, validate_config
from src.cost_model import check_policy

VIETNAM = timezone(timedelta(hours=7))


def uniform_baseline(config, budget_gb=None, *, training_scenario=None,
                     development_seed=None, locked_at=None):
    validate_config(config)
    dev = config["splits"]["development"]
    scenario = dev["scenarios"][0] if training_scenario is None else training_scenario
    seed = dev["seeds"][0] if development_seed is None else development_seed
    if scenario not in dev["scenarios"] or type(seed) is not int or seed not in dev["seeds"]:
        raise ValueError("baseline policy metadata must identify a development scenario/seed")
    budget = config["budget"]["main_gb"] if budget_gb is None else budget_gb
    finite_number(budget, "budget_gb")
    if locked_at is None:
        locked_at = datetime.now(VIETNAM).isoformat(timespec="seconds")
    elif (not isinstance(locked_at, str) or
          datetime.fromisoformat(locked_at).utcoffset() != timedelta(hours=7)):
        raise ValueError("locked_at must be ISO 8601 with offset +07:00")
    profiles = config["profiles"]
    chosen = None
    for ttl in reversed(config["ttl_grid_days"]):
        vector = {p["table_id"]: ttl for p in profiles}
        if check_policy(vector, config, budget)["feasible"]:
            chosen = vector
            break
    result = {
        "policy_id": f"baseline-{scenario}-dev{seed}-B{budget:g}",
        "kind": "baseline_uniform", "ttl_days": chosen or {},
        "budget_gb": budget, "config_hash": config_hash(config),
        "locked_on_split": "development", "training_scenario": scenario,
        "development_seed": seed, "locked_at": locked_at,
        "selection_inputs": "config profiles/grid/budget only; no incidents",
    }
    if chosen is None:
        result.update(status="infeasible", feasible=False, cost_gb=None,
                      coverage_claim_allowed=False, remaining_budget_gb=None,
                      violations=[{"code": "no_feasible_uniform_ttl"}])
    else:
        result.update(check_policy(chosen, config, budget))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiment.sample.json")
    parser.add_argument("--budget", type=float)
    parser.add_argument("--scenario", help="development scenario for policy metadata")
    parser.add_argument("--seed", type=int, help="development seed for policy metadata")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--output", help="write new JSON file exclusively; never overwrite")
    args = parser.parse_args()
    try:
        if args.sweep and args.budget is not None:
            raise ValueError("choose --sweep or --budget")
        config = load_config(args.config)
        budgets = config["budget"]["sweep_gb"] if args.sweep else [args.budget]
        policies = [uniform_baseline(config, budget, training_scenario=args.scenario,
                                     development_seed=args.seed) for budget in budgets]
        result = {"policies": policies} if args.sweep else policies[0]
        payload = json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
        if args.output:
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8", newline="\n") as output:
                output.write(payload)
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        parser.exit(2, f"Baseline selection failed: {error}\n")
    print(payload, end="")
    if not all(policy["feasible"] for policy in policies):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
