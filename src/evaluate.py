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
    for field in ("status", "note"):
        canonical.get("meta", {}).pop(field, None)
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def recoverable(incident: dict[str, Any], ttl_days: dict[str, float]) -> bool:
    """Apply the contract's inclusive, idealized recovery rule."""
    return (
        not incident["infrastructure_lost"]
        and incident["target_age_days"] <= ttl_days[incident["table_id"]]
    )


def _profiles(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {profile["table_id"]: profile for profile in config["profiles"]}


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
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 for value in parts):
            raise ValueError(f"incident {index} ages must be non-negative numbers")
        if not math.isclose(sum(parts[:3]), parts[3], rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"incident {incident['incident_id']} has H != A + D + L")
    keys = {(item["split"], item["scenario"], item["seed"]) for item in checked}
    if len(keys) != 1:
        raise ValueError("one metrics record must contain one split/scenario/seed")
    return checked


def _policy_metrics(
    config: dict[str, Any], incidents: list[dict[str, Any]], policy: dict[str, Any]
) -> dict[str, Any]:
    profiles = _profiles(config)
    ttl = policy.get("ttl_days", {})
    reasons: list[str] = []
    keys_valid = isinstance(ttl, dict) and set(ttl) == set(profiles)
    values_valid = keys_valid and all(
        not isinstance(value, bool) and isinstance(value, (int, float)) and value >= 0
        for value in ttl.values()
    )
    if not keys_valid:
        reasons.append("ttl_days must contain exactly the configured profiles")
    elif not values_valid:
        reasons.append("TTL values must be non-negative numbers")

    min_violations = [
        name for name in profiles
        if ttl[name] < profiles[name]["min_ttl_days"]
    ] if values_valid else []
    if min_violations:
        reasons.append("minimum TTL violated: " + ", ".join(min_violations))

    cost = policy_cost(config, ttl) if values_valid else 0.0
    declared_cost = policy.get("cost_gb")
    if (
        isinstance(declared_cost, bool)
        or not isinstance(declared_cost, (int, float))
        or not math.isclose(declared_cost, cost, rel_tol=0, abs_tol=1e-9)
    ):
        reasons.append(f"declared cost_gb does not match computed cost {cost:g}")
    budget = policy.get("budget_gb")
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget < 0:
        reasons.append("budget_gb must be a non-negative number")
        budget = 0.0
    budget_violations = int(cost > budget + 1e-9)
    if budget_violations:
        reasons.append(f"cost {cost:g} exceeds budget {budget:g}")
    if policy.get("feasible") is not True:
        reasons.append("policy is not feasible")

    by_profile: dict[str, list[bool]] = defaultdict(list)
    outcomes: list[bool] = []
    for incident in incidents:
        outcome = not reasons and recoverable(incident, ttl)
        outcomes.append(outcome)
        by_profile[incident["table_id"]].append(outcome)
    logical = [outcome for outcome, item in zip(outcomes, incidents) if not item["infrastructure_lost"]]
    infra = [outcome for outcome, item in zip(outcomes, incidents) if item["infrastructure_lost"]]

    def coverage(values: list[bool]) -> float | None:
        return sum(values) / len(values) if values else None

    return {
        "valid": not reasons,
        "invalid_reasons": reasons,
        "coverage_total": coverage(outcomes),
        "coverage_by_profile": {name: coverage(values) for name, values in sorted(by_profile.items())},
        "recoverable": sum(outcomes),
        "total": len(outcomes),
        "coverage_logical_only": coverage(logical),
        "coverage_infra_loss": coverage(infra),
        "cost_gb": cost,
        "budget_gb": budget,
        "budget_remaining_gb": budget - cost,
        "budget_violations": budget_violations,
        "min_ttl_violations": len(min_violations),
        "ttl_days": ttl,
        "failure_counts": {
            "infrastructure_lost": sum(item["infrastructure_lost"] for item in incidents),
            "ttl_expired": sum(
                not item["infrastructure_lost"] and not outcome
                for item, outcome in zip(incidents, outcomes)
            ),
        },
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
    policy_ids = [policy.get("policy_id") for policy in policy_list]
    if any(not isinstance(policy_id, str) or not policy_id for policy_id in policy_ids):
        raise ValueError("every policy needs a non-empty policy_id")
    if len(set(policy_ids)) != len(policy_ids):
        raise ValueError("policy_id values must be unique")
    for policy in policy_list:
        if policy.get("config_hash") != expected_hash:
            raise ValueError(f"policy {policy.get('policy_id')} config_hash mismatch")
        if policy.get("locked_on_split") != "development":
            raise ValueError(f"policy {policy.get('policy_id')} was not locked on development")
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
    valid = baseline_result["valid"] and optimized_result["valid"]
    split, scenario, seed = checked[0]["split"], checked[0]["scenario"], checked[0]["seed"]
    delta = None
    if valid:
        delta = 100 * (
            optimized_result["coverage_total"] - baseline_result["coverage_total"]
        )
    return {
        "run_id": run_id,
        "config_hash": expected_hash,
        "status": "valid" if valid else "invalid",
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
        "failure_cases": [
            "Infrastructure loss is never recoverable without an independent backup."
        ],
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
    config = _read_json(args.config)
    try:
        metrics = evaluate_pair(
            config,
            _read_jsonl(args.incidents),
            [_read_json(path) for path in args.policy],
            args.run_id,
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        metrics = {
            "run_id": args.run_id,
            "config_hash": config_hash(config),
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
