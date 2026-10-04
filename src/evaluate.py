"""Independent evaluator for the idealized TTL recovery model."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def config_hash(config: dict[str, Any]) -> str:
    canonical = json.loads(json.dumps(config))
    meta = canonical.get("meta", {})
    if not isinstance(meta, dict):
        raise ValueError("config.meta must be an object")
    for field in ("status", "note"):
        meta.pop(field, None)
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _finite_number(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def recoverable(incident: dict[str, Any], ttl_days: dict[str, float]) -> bool:
    """Apply the contract's inclusive, idealized recovery rule."""
    return (
        not incident["infrastructure_lost"]
        and incident["target_age_days"] <= ttl_days[incident["table_id"]]
    )


def _profiles(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = config.get("profiles")
    if not isinstance(items, list) or not items:
        raise ValueError("config.profiles must be a non-empty list")
    profiles: dict[str, dict[str, Any]] = {}
    for index, profile in enumerate(items):
        if not isinstance(profile, dict):
            raise ValueError(f"config.profiles[{index}] must be an object")
        table_id = profile.get("table_id")
        if not isinstance(table_id, str) or not table_id:
            raise ValueError(f"config.profiles[{index}].table_id must be a non-empty string")
        if table_id in profiles:
            raise ValueError(f"duplicate profile table_id: {table_id}")
        for field in ("history_gb_per_day", "min_ttl_days"):
            if not _finite_number(profile.get(field)) or profile[field] < 0:
                raise ValueError(f"profile {table_id}.{field} must be a finite non-negative number")
        profiles[table_id] = profile
    return profiles


def policy_cost(config: dict[str, Any], ttl_days: dict[str, float]) -> float:
    profiles = _profiles(config)
    return sum(profiles[name]["history_gb_per_day"] * ttl for name, ttl in ttl_days.items())


def _validate_incidents(
    incidents: Iterable[dict[str, Any]], profiles: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    checked = list(incidents)
    if not checked:
        raise ValueError("incidents must not be empty")
    seen: set[str] = set()
    required = {
        "incident_id", "split", "scenario", "seed", "table_id",
        "anchor_gap_days", "detect_delay_days", "response_lag_days",
        "target_age_days", "infrastructure_lost",
    }
    for index, incident in enumerate(checked):
        if not isinstance(incident, dict):
            raise ValueError(f"incident {index} must be an object")
        missing = required - incident.keys()
        if missing:
            raise ValueError(f"incident {index} missing fields: {sorted(missing)}")
        if not isinstance(incident["incident_id"], str) or not incident["incident_id"]:
            raise ValueError(f"incident {index} needs a non-empty incident_id")
        if incident["incident_id"] in seen:
            raise ValueError(f"duplicate incident_id: {incident['incident_id']}")
        seen.add(incident["incident_id"])
        if incident["split"] not in {"development", "holdout", "shift"}:
            raise ValueError(f"incident {index} has invalid split")
        if not isinstance(incident["scenario"], str) or not incident["scenario"]:
            raise ValueError(f"incident {index} needs a non-empty scenario")
        if isinstance(incident["seed"], bool) or not isinstance(incident["seed"], int):
            raise ValueError(f"incident {index} seed must be an integer")
        if incident["table_id"] not in profiles:
            raise ValueError(f"unknown table_id: {incident['table_id']}")
        if not isinstance(incident["infrastructure_lost"], bool):
            raise ValueError("infrastructure_lost must be boolean")
        parts = [incident[name] for name in (
            "anchor_gap_days", "detect_delay_days", "response_lag_days", "target_age_days"
        )]
        if any(not _finite_number(value) or value < 0 for value in parts):
            raise ValueError(f"incident {index} ages must be finite non-negative numbers")
        if not math.isclose(sum(parts[:3]), parts[3], rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"incident {incident['incident_id']} has H != A + D + L")
    keys = {(item["split"], item["scenario"], item["seed"]) for item in checked}
    if len(keys) != 1:
        raise ValueError("one metrics record must contain one split/scenario/seed")
    return checked

def _expected_training(
    config: dict[str, Any], split: str, scenario: str, seed: int
) -> tuple[str, int]:
    splits = config.get("splits")
    if not isinstance(splits, dict):
        raise ValueError("config.splits must be an object")
    split_config = splits.get(split)
    if not isinstance(split_config, dict):
        raise ValueError(f"split {split} is not declared in config")
    scenarios = split_config.get("scenarios")
    seeds = split_config.get("seeds")
    if not isinstance(scenarios, list) or not isinstance(seeds, list):
        raise ValueError(f"config split {split} needs scenario and seed lists")
    if scenario not in scenarios:
        raise ValueError(f"scenario {scenario} is not declared for split {split}")
    if seed not in seeds:
        raise ValueError(f"seed {seed} is not declared for split {split}")
    if split == "development":
        return scenario, seed
    routes = config.get("evaluation_routing")
    if not isinstance(routes, list):
        raise ValueError("config.evaluation_routing must be a list")
    matches = [
        route for route in routes
        if isinstance(route, dict)
        and route.get("evaluation_split") == split
        and route.get("evaluation_scenario") == scenario
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one evaluation route for {split}/{scenario}")
    route = matches[0]
    training_scenario = route.get("development_scenario")
    offset = route.get("development_seed_offset")
    if not isinstance(training_scenario, str) or not training_scenario:
        raise ValueError("evaluation route needs development_scenario")
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise ValueError("evaluation route needs integer development_seed_offset")
    return training_scenario, seed + offset


def _policy_metrics(
    config: dict[str, Any], incidents: list[dict[str, Any]], policy: dict[str, Any]
) -> dict[str, Any]:
    profiles = _profiles(config)
    ttl = policy.get("ttl_days", {})
    reasons: list[str] = []
    keys_valid = isinstance(ttl, dict) and set(ttl) == set(profiles)
    values_valid = keys_valid and all(
        _finite_number(value) and value >= 0 for value in ttl.values()
    )
    if not keys_valid:
        reasons.append("ttl_days must contain exactly the configured profiles")
    elif not values_valid:
        reasons.append("TTL values must be finite non-negative numbers")

    min_violations = [
        name for name in profiles
        if ttl[name] < profiles[name]["min_ttl_days"]
    ] if values_valid else []
    if min_violations:
        reasons.append("minimum TTL violated: " + ", ".join(min_violations))

    grid = config.get("ttl_grid_days")
    if (
        not isinstance(grid, list)
        or not grid
        or any(not _finite_number(value) or value < 0 for value in grid)
    ):
        raise ValueError("config.ttl_grid_days must contain finite non-negative numbers")
    grid_violations = [name for name in profiles if values_valid and ttl[name] not in grid]
    if grid_violations:
        reasons.append("TTL outside configured grid: " + ", ".join(grid_violations))

    cost = policy_cost(config, ttl) if values_valid else 0.0
    declared_cost = policy.get("cost_gb")
    if not _finite_number(declared_cost) or not math.isclose(
        declared_cost, cost, rel_tol=0, abs_tol=1e-9
    ):
        reasons.append(f"declared cost_gb does not match computed cost {cost:g}")
    budget = policy.get("budget_gb")
    if not _finite_number(budget) or budget < 0:
        reasons.append("budget_gb must be a non-negative number")
        budget = 0.0
    budget_violations = int(cost > budget + 1e-9)
    if budget_violations:
        reasons.append(f"cost {cost:g} exceeds budget {budget:g}")
    if policy.get("feasible") is not True:
        reasons.append("policy is not feasible")

    def coverage(values: list[bool]) -> float | None:
        return sum(values) / len(values) if values else None

    policy_valid = not reasons
    profile_names = sorted({incident["table_id"] for incident in incidents})
    if policy_valid:
        by_profile: dict[str, list[bool]] = defaultdict(list)
        outcomes = []
        for incident in incidents:
            outcome = recoverable(incident, ttl)
            outcomes.append(outcome)
            by_profile[incident["table_id"]].append(outcome)
        logical = [
            outcome for outcome, item in zip(outcomes, incidents)
            if not item["infrastructure_lost"]
        ]
        infra = [
            outcome for outcome, item in zip(outcomes, incidents)
            if item["infrastructure_lost"]
        ]
        coverage_total = coverage(outcomes)
        coverage_by_profile = {
            name: coverage(by_profile[name]) for name in profile_names
        }
        recoverable_count: int | None = sum(outcomes)
        logical_coverage = coverage(logical)
        infra_coverage = coverage(infra)
        ttl_expired: int | None = sum(
            not item["infrastructure_lost"] and not outcome
            for item, outcome in zip(incidents, outcomes)
        )
    else:
        coverage_total = logical_coverage = infra_coverage = None
        coverage_by_profile = {name: None for name in profile_names}
        recoverable_count = ttl_expired = None

    return {
        "valid": policy_valid,
        "invalid_reasons": reasons,
        "coverage_total": coverage_total,
        "coverage_by_profile": coverage_by_profile,
        "recoverable": recoverable_count,
        "total": len(incidents),
        "coverage_logical_only": logical_coverage,
        "coverage_infra_loss": infra_coverage,
        "cost_gb": cost,
        "budget_gb": budget,
        "budget_remaining_gb": budget - cost,
        "budget_violations": budget_violations,
        "min_ttl_violations": len(min_violations),
        "grid_violations": len(grid_violations),
        "ttl_days": ttl,
        "failure_counts": {
            "infrastructure_lost": sum(item["infrastructure_lost"] for item in incidents),
            "ttl_expired": ttl_expired,
        },
    }


def evaluate_policy(
    config: dict[str, Any], policy: dict[str, Any], incidents: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    """Evaluate one policy using the compact API retained by the MVP tests."""
    if not isinstance(policy, dict):
        raise ValueError("policy must be an object")
    profiles = _profiles(config)
    checked = list(incidents)
    required = {
        "incident_id",
        "table_id",
        "anchor_gap_days",
        "detect_delay_days",
        "response_lag_days",
        "target_age_days",
        "infrastructure_lost",
    }
    for index, incident in enumerate(checked):
        if not isinstance(incident, dict):
            raise ValueError(f"incident {index} must be an object")
        missing = required - incident.keys()
        if missing:
            raise ValueError(f"incident {index} missing fields: {sorted(missing)}")
        if incident["table_id"] not in profiles:
            raise ValueError(f"unknown table_id: {incident['table_id']}")
        if not isinstance(incident["infrastructure_lost"], bool):
            raise ValueError("infrastructure_lost must be boolean")
        ages = [
            incident["anchor_gap_days"],
            incident["detect_delay_days"],
            incident["response_lag_days"],
            incident["target_age_days"],
        ]
        if any(not _finite_number(value) or value < 0 for value in ages):
            raise ValueError(f"incident {index} ages must be finite non-negative numbers")
        if not math.isclose(sum(ages[:3]), ages[3], rel_tol=0, abs_tol=1e-6):
            raise ValueError(
                f"incident {incident['incident_id']} has H != A + D + L"
            )

    ttl = policy.get("ttl_days")
    adapted_config = dict(config)
    if "ttl_grid_days" not in adapted_config:
        finite_ttls = (
            sorted({value for value in ttl.values() if _finite_number(value)})
            if isinstance(ttl, dict)
            else []
        )
        adapted_config["ttl_grid_days"] = finite_ttls or [0]

    adapted_policy = dict(policy)
    if "cost_gb" not in adapted_policy:
        ttl_keys_valid = isinstance(ttl, dict) and set(ttl) == set(profiles)
        ttl_values_valid = ttl_keys_valid and all(
            _finite_number(value) and value >= 0 for value in ttl.values()
        )
        adapted_policy["cost_gb"] = (
            policy_cost(config, ttl) if ttl_values_valid else 0.0
        )

    metrics = _policy_metrics(adapted_config, checked, adapted_policy)
    return {
        "status": "valid" if metrics["valid"] else "invalid",
        "metrics": metrics,
    }


def evaluate_pair(
    config: dict[str, Any],
    incidents: Iterable[dict[str, Any]],
    policies: Iterable[dict[str, Any]],
    run_id: str,
) -> dict[str, Any]:
    """Evaluate policies on the same incidents and return one contract metrics record."""
    profiles = _profiles(config)
    checked = _validate_incidents(incidents, profiles)
    expected_hash = config_hash(config)
    policy_list = list(policies)
    if len(policy_list) != 2:
        raise ValueError("exactly baseline and optimized policies are required")
    if any(not isinstance(policy, dict) for policy in policy_list):
        raise ValueError("every policy must be an object")
    policy_ids = [policy.get("policy_id") for policy in policy_list]
    if any(not isinstance(policy_id, str) or not policy_id for policy_id in policy_ids):
        raise ValueError("every policy needs a non-empty policy_id")
    if len(set(policy_ids)) != len(policy_ids):
        raise ValueError("policy_id values must be unique")
    split, scenario, seed = checked[0]["split"], checked[0]["scenario"], checked[0]["seed"]
    training_scenario, development_seed = _expected_training(config, split, scenario, seed)
    for policy in policy_list:
        if policy.get("config_hash") != expected_hash:
            raise ValueError(f"policy {policy.get('policy_id')} config_hash mismatch")
        if policy.get("locked_on_split") != "development":
            raise ValueError(f"policy {policy.get('policy_id')} was not locked on development")
        if policy.get("training_scenario") != training_scenario:
            raise ValueError(f"policy {policy.get('policy_id')} training_scenario mismatch")
        if policy.get("development_seed") != development_seed:
            raise ValueError(f"policy {policy.get('policy_id')} development_seed mismatch")
    metrics = {
        policy["policy_id"]: _policy_metrics(config, checked, policy)
        for policy in policy_list
    }
    baseline = next((p for p in policy_list if p.get("kind") == "baseline_uniform"), None)
    optimized = next((p for p in policy_list if p.get("kind") == "optimized_per_profile"), None)
    if not baseline or not optimized:
        raise ValueError("one baseline_uniform and one optimized_per_profile policy are required")
    baseline_result = metrics[baseline["policy_id"]]
    optimized_result = metrics[optimized["policy_id"]]

    pair_reasons: list[str] = []
    budgets = [policy.get("budget_gb") for policy in policy_list]
    if all(_finite_number(budget) for budget in budgets) and not math.isclose(
        budgets[0], budgets[1], rel_tol=0, abs_tol=1e-9
    ):
        pair_reasons.append("policies must use the same budget_gb")
    budget_config = config.get("budget")
    if not isinstance(budget_config, dict):
        raise ValueError("config.budget must be an object")
    sweep_budgets = budget_config.get("sweep_gb")
    if not isinstance(sweep_budgets, list):
        raise ValueError("config.budget.sweep_gb must be a list")
    allowed_budgets = [budget_config.get("main_gb"), *sweep_budgets]
    if any(
        not _finite_number(value) or value < 0
        for value in allowed_budgets
    ):
        raise ValueError("configured budgets must be finite non-negative numbers")
    if all(_finite_number(budget) for budget in budgets) and any(
        not any(math.isclose(budget, allowed, rel_tol=0, abs_tol=1e-9) for allowed in allowed_budgets)
        for budget in budgets
    ):
        pair_reasons.append("policy budget_gb is not declared in config")
    for reason in pair_reasons:
        for result in metrics.values():
            result["valid"] = False
            result["invalid_reasons"].append(reason)

    valid = baseline_result["valid"] and optimized_result["valid"]
    invalid_reasons = [
        f"{policy_id}: {reason}"
        for policy_id, result in metrics.items()
        for reason in result["invalid_reasons"]
    ]
    delta = 100 * (
        optimized_result["coverage_total"] - baseline_result["coverage_total"]
    ) if valid else None
    failure_cases = []
    if any(item["infrastructure_lost"] for item in checked):
        failure_cases.append("Infrastructure loss is never recoverable without an independent backup.")
    for policy_id, result in metrics.items():
        expired = result["failure_counts"]["ttl_expired"]
        if result["valid"] and expired:
            failure_cases.append(f"{policy_id}: {expired} logical incidents exceeded TTL.")
    if not failure_cases:
        failure_cases.append("No recovery failure was observed in this evaluation record.")
    return {
        "run_id": run_id,
        "config_hash": expected_hash,
        "status": "valid" if valid else "invalid",
        "invalid_reasons": invalid_reasons,
        "split": split,
        "scenario": scenario,
        "seed": seed,
        "incident_count": len(checked),
        "profile_count": len(profiles),
        "model_assumption": "Idealized TTL model: no infrastructure loss and H <= TTL.",
        "policies": metrics,
        "paired": {
            "baseline_policy_id": baseline["policy_id"],
            "optimized_policy_id": optimized["policy_id"],
            "delta_pp": delta,
        },
        "aggregate": None,
        "failure_cases": failure_cases,
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate two locked retention policies")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--incidents", type=Path, required=True)
    parser.add_argument("--policy", type=Path, action="append", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config: dict[str, Any] | None = None
    fingerprint: str | None = None
    try:
        loaded_config = _read_json(args.config)
        if not isinstance(loaded_config, dict):
            raise ValueError("config must be a JSON object")
        config = loaded_config
        fingerprint = config_hash(config)
        metrics = evaluate_pair(
            config,
            _read_jsonl(args.incidents),
            [_read_json(path) for path in args.policy],
            args.run_id,
        )
    except (OSError, AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        metrics = {
            "run_id": args.run_id,
            "config_hash": fingerprint,
            "status": "invalid",
            "invalid_reasons": [str(error)],
            "policies": {},
            "paired": {"delta_pp": None},
            "failure_cases": [],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    if metrics["status"] != "valid":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
