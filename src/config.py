"""Load and fingerprint the single experiment config; reject unsupported models."""
import copy
import hashlib
import json
import math
import re
from pathlib import Path


def finite_number(value, name, *, positive=False):
    try:
        valid = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid or value < 0 or (positive and value == 0):
        raise ValueError(f"{name} must be a finite {'positive' if positive else 'nonnegative'} number")
    return value


def validate_cost_config(config):
    profiles = config["profiles"]
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("profiles must be a nonempty list")
    ids = []
    for profile in profiles:
        table = profile["table_id"]
        if not isinstance(table, str) or not re.fullmatch(r"[A-Za-z0-9_]+", table):
            raise ValueError("table_id must be a nonempty ASCII identifier")
        ids.append(table)
        finite_number(profile["history_gb_per_day"], f"{table}.history_gb_per_day", positive=True)
        finite_number(profile["min_ttl_days"], f"{table}.min_ttl_days")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate table_id")
    grid = config["ttl_grid_days"]
    if not isinstance(grid, list) or not grid:
        raise ValueError("ttl_grid_days must be a nonempty list")
    for ttl in grid:
        finite_number(ttl, "grid TTL", positive=True)
    if grid != sorted(set(grid)):
        raise ValueError("ttl_grid_days must be sorted and unique")
    if config["budget"]["kind"] != "history_overhead":
        raise ValueError("budget must measure extra history overhead")
    finite_number(config["budget"]["main_gb"], "budget.main_gb")
    for budget in config["budget"]["sweep_gb"]:
        finite_number(budget, "sweep budget")
    return config


def validate_distribution(spec, name):
    if spec.get("kind") == "mixture":
        components = spec["components"]
        if not isinstance(components, list) or not components:
            raise ValueError(f"{name}: mixture must have components")
        weights = []
        for component in components:
            weights.append(finite_number(component["weight"], f"{name}.weight"))
            validate_distribution(component, name)
        if not math.isclose(sum(weights), 1, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"{name}: mixture weights must sum to 1")
    elif spec.get("dist") == "constant":
        finite_number(spec["value"], f"{name}.value")
    elif spec.get("dist") == "uniform":
        low = finite_number(spec["low"], f"{name}.low")
        high = finite_number(spec["high"], f"{name}.high")
        if low >= high:
            raise ValueError(f"{name}: uniform requires low < high")
    else:
        raise ValueError(f"{name}: unsupported distribution")


def validate_config(config):
    validate_cost_config(config)
    n = config["incidents_per_profile"]
    if type(n) is not int or n <= 0:
        raise ValueError("incidents_per_profile must be a positive integer")
    if config["rng"] != {"library": "numpy.random.default_rng",
                         "seed_sequence_entropy": ["seed", "scenario_index", "profile_index"]}:
        raise ValueError("unsupported RNG configuration")
    ids = [p["table_id"] for p in config["profiles"]]
    for profile in config["profiles"]:
        validate_distribution(profile["detect_delay_days"], profile["table_id"])
    age_keys = ("anchor_gap_days_A", "response_lag_days_L")
    for key in age_keys:
        validate_distribution(config["version_age"][key], key)
    scenario_ids = []
    allowed_overrides = {f"{table}.detect_delay_days" for table in ids}
    allowed_overrides.update(f"version_age.{key}" for key in age_keys)
    for scenario in config["scenarios"]:
        sid = scenario["id"]
        if not isinstance(sid, str) or not re.fullmatch(r"[A-Za-z0-9_]+", sid):
            raise ValueError("invalid scenario ID")
        scenario_ids.append(sid)
        rate = finite_number(scenario["infra_loss_rate"], f"{sid}.infra_loss_rate")
        if rate > 1 or not math.isclose(n * rate, round(n * rate), rel_tol=0, abs_tol=1e-9):
            raise ValueError(f"{sid}: fixed infrastructure-loss count must be an integer in [0,n]")
        for key, spec in scenario["overrides"].items():
            if key not in allowed_overrides:
                raise ValueError(f"unsupported override: {key}")
            validate_distribution(spec, key)
    if not scenario_ids or len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("scenarios must be nonempty with unique IDs")
    if set(config["splits"]) != {"development", "holdout", "shift"}:
        raise ValueError("splits must be development, holdout and shift")
    seen_seeds = set()
    for split, spec in config["splits"].items():
        seeds = spec["seeds"]
        if (not isinstance(seeds, list) or not seeds or
                any(type(seed) is not int or seed < 0 for seed in seeds) or
                len(set(seeds)) != len(seeds) or seen_seeds.intersection(seeds)):
            raise ValueError("split seeds must be unique nonnegative integers and disjoint")
        seen_seeds.update(seeds)
        scenarios = spec["scenarios"]
        if (not isinstance(scenarios, list) or not scenarios or
                len(set(scenarios)) != len(scenarios) or not set(scenarios) <= set(scenario_ids)):
            raise ValueError(f"{split}: invalid scenarios")
        if spec["optimizer_may_read"] is not (split == "development"):
            raise ValueError("optimizer may only read development")
    return config


def load_config(path="configs/experiment.sample.json"):
    return validate_config(json.loads(Path(path).read_text(encoding="utf-8-sig")))


def config_hash(config):
    canonical = copy.deepcopy(config)
    for field in ("status", "note"):
        canonical["meta"].pop(field, None)
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
