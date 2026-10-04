"""Reproducible synthetic incidents using contract RNG streams (TASK-05)."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

from src.config import config_hash, load_config, validate_config
from src.fixture_contract import validate_incidents

GENERATOR_VERSION = "1.0"


def _sample(spec, rng, count):
    if spec.get("kind") == "mixture":
        components = spec["components"]
        weights = np.asarray([part["weight"] for part in components], dtype=np.float64)
        membership = rng.choice(len(components), size=count, p=weights / weights.sum())
        values = np.empty(count, dtype=np.float64)
        for index, component in enumerate(components):
            mask = membership == index
            values[mask] = _sample(component, rng, int(mask.sum()))
        return values
    if spec["dist"] == "constant":
        return np.full(count, spec["value"], dtype=np.float64)
    if spec["dist"] == "uniform":
        return rng.uniform(spec["low"], spec["high"], size=count)
    raise ValueError("unsupported distribution")


def _request(config, split, scenario, seed):
    if split not in config["splits"]:
        raise ValueError("unknown split")
    spec = config["splits"][split]
    if scenario not in spec["scenarios"] or type(seed) is not int or seed not in spec["seeds"]:
        raise ValueError("scenario/seed must be declared for this split")


def generate_incidents(config, split, scenario, seed):
    """One dataset in profile order, with one independent RNG per profile.

    Zero-based scenario/profile indexes refer to the ordered config lists.
    Sampling order is A, D, L, then fixed-count infrastructure selection.
    Mixture membership is random, not forced to the nominal proportions.
    """
    validate_config(config)
    _request(config, split, scenario, seed)
    scenario_index, scenario_spec = next(
        (index, spec) for index, spec in enumerate(config["scenarios"]) if spec["id"] == scenario)
    overrides = scenario_spec["overrides"]
    count = config["incidents_per_profile"]
    lost_count = round(count * scenario_spec["infra_loss_rate"])
    events = []
    for profile_index, profile in enumerate(config["profiles"]):
        table = profile["table_id"]
        rng = np.random.default_rng(np.random.SeedSequence([seed, scenario_index, profile_index]))
        anchor = _sample(overrides.get("version_age.anchor_gap_days_A",
                                       config["version_age"]["anchor_gap_days_A"]), rng, count)
        delay = _sample(overrides.get(f"{table}.detect_delay_days",
                                      profile["detect_delay_days"]), rng, count)
        lag = _sample(overrides.get("version_age.response_lag_days_L",
                                    config["version_age"]["response_lag_days_L"]), rng, count)
        lost = np.zeros(count, dtype=bool)
        if lost_count:
            lost[rng.choice(count, size=lost_count, replace=False)] = True
        for index in range(count):
            a, d, lag_days = float(anchor[index]), float(delay[index]), float(lag[index])
            events.append({
                "incident_id": f"{split}-{scenario}-s{seed}-{table}-{index + 1:04d}",
                "split": split, "scenario": scenario, "seed": seed, "table_id": table,
                "anchor_gap_days": a, "detect_delay_days": d, "response_lag_days": lag_days,
                "target_age_days": a + d + lag_days, "infrastructure_lost": bool(lost[index]),
            })
    return validate_incidents(events, config)


def incidents_jsonl(incidents):
    return "".join(json.dumps(event, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":"), allow_nan=False) + "\n" for event in incidents)


def _describe(values):
    array = np.asarray(values, dtype=np.float64)
    return {
        "min": float(array.min()), "mean": float(array.mean()),
        "std_population": float(array.std(ddof=0)), "median": float(np.median(array)),
        "p90": float(np.quantile(array, .9)), "p95": float(np.quantile(array, .95)),
        "max": float(array.max()),
    }


def summarize_incidents(incidents, config):
    validate_incidents(incidents, config)
    keys = {(e["split"], e["scenario"], e["seed"]) for e in incidents}
    if len(keys) != 1:
        raise ValueError("summarize one split/scenario/seed dataset at a time")
    split, scenario, seed = next(iter(keys))
    profiles = {}
    for profile in config["profiles"]:
        table = profile["table_id"]
        subset = [event for event in incidents if event["table_id"] == table]
        if len(subset) != config["incidents_per_profile"]:
            raise ValueError("dataset must contain incidents_per_profile for every profile")
        lost = sum(event["infrastructure_lost"] for event in subset)
        profiles[table] = {
            "count": len(subset), "infrastructure_lost": lost, "infra_loss_rate": lost / len(subset),
            "detect_delay_days": _describe([e["detect_delay_days"] for e in subset]),
            "response_lag_days": _describe([e["response_lag_days"] for e in subset]),
            "target_age_days": _describe([e["target_age_days"] for e in subset]),
        }
    return {"split": split, "scenario": scenario, "seed": seed, "count": len(incidents),
            "profiles": profiles}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiment.sample.json")
    parser.add_argument("--split", choices=("development", "holdout", "shift"))
    parser.add_argument("--scenario")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--all", action="store_true", help="generate all configured datasets")
    parser.add_argument("--output-dir", required=True, help="new directory; never overwrite an old dataset")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.all:
            if any(value is not None for value in (args.split, args.scenario, args.seed)):
                raise ValueError("--all cannot be combined with --split/--scenario/--seed")
            requests = [(split, scenario, seed) for split, spec in config["splits"].items()
                        for scenario in spec["scenarios"] for seed in spec["seeds"]]
        else:
            split = args.split or "development"
            spec = config["splits"][split]
            requests = [(split, args.scenario or spec["scenarios"][0],
                         spec["seeds"][0] if args.seed is None else args.seed)]
        for request in requests:
            _request(config, *request)
        directory = Path(args.output_dir)
        directory.mkdir(parents=True, exist_ok=False)
        manifest = {
            "generator_version": GENERATOR_VERSION, "config_hash": config_hash(config),
            "python_version": platform.python_version(), "numpy_version": np.__version__,
            "dataset_count": len(requests), "datasets": [],
            "scope": "synthetic data generation/statistics only; no recovery evaluation",
        }
        for split, scenario, seed in requests:
            incidents = generate_incidents(config, split, scenario, seed)
            payload = incidents_jsonl(incidents).encode("utf-8")
            filename = f"{split}-{scenario}-s{seed}.jsonl"
            (directory / filename).write_bytes(payload)
            summary = summarize_incidents(incidents, config)
            summary.update(file=filename, sha256=hashlib.sha256(payload).hexdigest())
            manifest["datasets"].append(summary)
        manifest["total_incidents"] = sum(dataset["count"] for dataset in manifest["datasets"])
        (directory / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False,
                                                           allow_nan=False, indent=2) + "\n",
                                                 encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        parser.exit(2, f"Generation failed: {error}\n")
    print(json.dumps({"status": "generated", "dataset_count": manifest["dataset_count"],
                      "total_incidents": manifest["total_incidents"],
                      "manifest": str(directory / "manifest.json"),
                      "config_hash": manifest["config_hash"]}))


if __name__ == "__main__":
    main()
