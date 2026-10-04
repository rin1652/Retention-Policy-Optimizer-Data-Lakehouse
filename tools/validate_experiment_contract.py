"""Validate TASK-01 assumptions; does not run lakehouse evaluation."""
import hashlib
import itertools
import json
import math
import tempfile
import uuid
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "configs/experiment.sample.json").read_text(encoding="utf-8"))
    contract = (root / "docs/experiment-contract.md").read_text(encoding="utf-8")
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    profiles = config["profiles"]
    ids = [p["table_id"] for p in profiles]
    grid = config["ttl_grid_days"]
    budget = config["budget"]["main_gb"]
    check("contract_version_1.0", config["meta"]["contract_version"] == "1.0")
    check("three_unique_profiles", ids == ["raw_ingest", "curated_business", "training_dataset"])
    check("positive_cost_and_minimum", all(p["history_gb_per_day"] > 0 and p["min_ttl_days"] > 0 for p in profiles))
    check("grid_sorted_unique_positive", grid == sorted(set(grid)) and all(t > 0 for t in grid))
    check("mixture_weights_and_bounds", all(
        math.isclose(sum(x["weight"] for x in p["detect_delay_days"]["components"]), 1.0)
        and all(x["weight"] >= 0 and 0 <= x["low"] < x["high"] for x in p["detect_delay_days"]["components"])
        for p in profiles
    ))

    def cost(vector):
        return sum(p["history_gb_per_day"] * t for p, t in zip(profiles, vector))

    def valid(vector, limit=budget):
        return all(t in grid and t >= p["min_ttl_days"] for p, t in zip(profiles, vector)) and cost(vector) <= limit

    vectors = list(itertools.product(grid, repeat=3))
    feasible = [v for v in vectors if valid(v)]
    baseline = max(t for t in grid if valid((t, t, t)))
    check("216_candidates_66_feasible", len(vectors) == 216 and len(feasible) == 66)
    check("baseline_30_days_810_GB", baseline == 30 and cost((baseline,) * 3) == budget == 810)
    check("fixture_cost_760_GB", valid((14, 60, 90)) and cost((14, 60, 90)) == 760)
    check("fixture_budget_violation", not valid((90, 90, 90)) and cost((90, 90, 90)) == 2430)
    check("fixture_minimum_violation", not valid((1, 7, 7)))
    check("minimum_vector_cost_83_GB", cost(tuple(p["min_ttl_days"] for p in profiles)) == 83)
    check("budget_300_uniform_infeasible", not any(valid((t, t, t), 300) for t in grid))

    def recoverable(age, ttl, infrastructure_lost=False):
        return not infrastructure_lost and age <= ttl

    check("fixture_boundary_and_infrastructure", [
        recoverable(0.5, 1), recoverable(1, 1), recoverable(1.5, 1), recoverable(0.1, 90, True)
    ] == [True, True, False, False])
    scenarios = {s["id"]: s for s in config["scenarios"]}
    check("900_incidents_and_24_infra_per_profile", config["incidents_per_profile"] * len(profiles) == 900
          and math.isclose(config["incidents_per_profile"] * scenarios["S1_infra_loss"]["infra_loss_rate"], 24))

    splits = config["splits"]
    check("disjoint_seed_sets", all(
        not set(splits[a]["seeds"]) & set(splits[b]["seeds"])
        for a, b in itertools.combinations(splits, 2)
    ))
    check("holdout_not_optimizer_input", splits["development"]["optimizer_may_read"]
          and not splits["holdout"]["optimizer_may_read"] and not splits["shift"]["optimizer_may_read"])
    expected_routes = {
        ("holdout", "S0_main"): ("S0_main", -1000),
        ("holdout", "S1_infra_loss"): ("S1_infra_loss", -1000),
        ("shift", "S2_tail_shift"): ("S0_main", -2000),
        ("shift", "S3_slow_response"): ("S0_main", -2000),
    }
    routes = {(r["evaluation_split"], r["evaluation_scenario"]):
              (r["development_scenario"], r["development_seed_offset"])
              for r in config["evaluation_routing"]}
    check("scenario_routing_exact", routes == expected_routes and len(config["evaluation_routing"]) == 4)
    check("seed_pairing_covers_all_runs", all(
        [seed + offset for seed in splits[split]["seeds"]] == splits["development"]["seeds"]
        for (split, _), (_, offset) in routes.items()
    ))
    check("aggregate_keeps_scenarios_separate", config["aggregate_group_by"] ==
          ["budget_gb", "evaluation_split", "evaluation_scenario"])

    # Demonstrate the contract's collision handling, including a forced collision.
    def allocate(parent, prefix, candidates):
        for suffix in candidates:
            directory = parent / (prefix + suffix)
            try:
                directory.mkdir(exist_ok=False)
                return directory
            except FileExistsError:
                continue
        raise RuntimeError("No unique run ID")

    with tempfile.TemporaryDirectory(prefix="task01-") as temporary:
        parent = Path(temporary)
        fixed = "0" * 32
        prefix = "20261005T102000-example-"
        first = allocate(parent, prefix, [fixed])
        (first / "marker.txt").write_text("previous run", encoding="utf-8")
        second = allocate(parent, prefix, [fixed, uuid.uuid4().hex])
        check("forced_run_id_collision_preserves_old_run", first != second and
              (first / "marker.txt").read_text(encoding="utf-8") == "previous run")
    check("uuid_and_exclusive_allocation_declared", "{uuid4_hex}" in config["run_id_format"] and
          config["run_id_allocation"] == "create_directory_exclusively_and_retry_with_new_uuid_on_collision")

    for token in ["810 GB", "66 vector", "S0 development", "UUID4", "evaluation_routing", "64 ký tự"]:
        check("contract_documents_" + token, token in contract)

    canonical = json.loads(json.dumps(config))
    for name in ["status", "note"]:
        canonical["meta"].pop(name, None)
    config_hash = hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True,
                                           separators=(",", ":")).encode("utf-8")).hexdigest()
    print(json.dumps({
        "status": "passed", "check_count": len(checks), "checks": checks,
        "baseline_ttl_days": baseline, "baseline_cost_gb": cost((baseline,) * 3),
        "feasible_vectors": len(feasible), "config_sha256": config_hash,
        "scope": "contract/config and hand fixtures only; no recovery experiment executed"
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
