"""Validate hand-authored integration incidents against contract v1.0.

This validates fixture structure, not sampling distributions or recovery metrics.
Generator and evaluator implementations belong to their respective issues.
"""
import argparse
import json
import math
import re
from pathlib import Path

FIELDS = {
    "incident_id", "split", "scenario", "seed", "table_id",
    "anchor_gap_days", "detect_delay_days", "response_lag_days",
    "target_age_days", "infrastructure_lost",
}
AGE_FIELDS = (
    "anchor_gap_days", "detect_delay_days", "response_lag_days", "target_age_days",
)


class FixtureValidationError(ValueError):
    """An integration fixture does not satisfy the shared incident contract."""


def validate_incidents(incidents, config):
    """Return incidents after validation; raise on any invalid input.

    Hand fixtures intentionally do not enforce 900 rows or an 8% incident mix.
    """
    if not isinstance(incidents, list) or not incidents:
        raise FixtureValidationError("Fixture must be a nonempty list of incidents")
    table_ids = {profile["table_id"] for profile in config["profiles"]}
    seen = set()
    for number, event in enumerate(incidents, 1):
        def fail(message):
            raise FixtureValidationError(f"Incident {number}: {message}")

        if not isinstance(event, dict):
            fail("must be a JSON object")
        if set(event) != FIELDS:
            fail(f"field mismatch; missing={sorted(FIELDS - set(event))}, "
                 f"unknown={sorted(set(event) - FIELDS)}")
        for field in ("incident_id", "split", "scenario", "table_id"):
            if not isinstance(event[field], str) or not event[field]:
                fail(f"{field} must be a nonempty string")
        if event["table_id"] not in table_ids:
            fail("unknown table_id")
        split = config["splits"].get(event["split"])
        if split is None:
            fail("unknown split")
        if event["scenario"] not in split["scenarios"]:
            fail("scenario is not allowed in this split")
        if type(event["seed"]) is not int or event["seed"] not in split["seeds"]:
            fail("seed must be an integer declared for this split")
        if type(event["infrastructure_lost"]) is not bool:
            fail("infrastructure_lost must be a JSON boolean")
        for field in AGE_FIELDS:
            value = event[field]
            finite = False
            if type(value) in (int, float):
                try:
                    finite = math.isfinite(value)
                except OverflowError:
                    pass
            if not finite or value < 0:
                fail(f"{field} must be finite and nonnegative, not a boolean")
        expected_age = sum(event[field] for field in AGE_FIELDS[:3])
        if not math.isclose(event["target_age_days"], expected_age, rel_tol=0, abs_tol=1e-9):
            fail("target_age_days must equal A + D + L (absolute tolerance 1e-9 days)")
        prefix = (f"{event['split']}-{event['scenario']}-s{event['seed']}-"
                  f"{event['table_id']}-")
        if not re.fullmatch(re.escape(prefix) + r"\d{4,}", event["incident_id"]):
            fail("incident_id must follow the contract format")
        if event["incident_id"] in seen:
            fail("duplicate incident_id")
        seen.add(event["incident_id"])
    return incidents


def read_fixture(path, config):
    incidents = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            incidents.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise FixtureValidationError(f"Invalid JSON at line {line_number}") from error
    return validate_incidents(incidents, config)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/experiment.sample.json")
    parser.add_argument("--fixture", default="tests/fixtures/incidents.sample.jsonl")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8-sig"))
        incidents = read_fixture(args.fixture, config)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Fixture validation failed: {error}\n")
    print(json.dumps({
        "status": "passed", "fixture_only": True, "incident_count": len(incidents),
        "table_ids": sorted({event["table_id"] for event in incidents}),
        "scope": "schema validation only; not a recovery experiment",
    }))


if __name__ == "__main__":
    main()
