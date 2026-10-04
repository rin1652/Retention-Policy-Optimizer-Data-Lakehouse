"""Protect the shared fixture schema and independent hand-calculated answers."""
import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.fixture_contract import FixtureValidationError, read_fixture, validate_incidents

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/experiment.sample.json"
FIXTURE = ROOT / "tests/fixtures/incidents.sample.jsonl"
EXPECTED = ROOT / "tests/fixtures/expected.sample.json"


class FixtureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.events = read_fixture(FIXTURE, cls.config)
        cls.expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

    def changed(self, **fields):
        event = copy.deepcopy(self.events[0])
        event.update(fields)
        return [event]

    def assert_invalid(self, events):
        with self.assertRaises(FixtureValidationError):
            validate_incidents(events, self.config)

    def test_valid_fixture_covers_three_profiles(self):
        self.assertEqual(len(self.events), 7)
        self.assertEqual({e["table_id"] for e in self.events},
                         {p["table_id"] for p in self.config["profiles"]})

    def test_duplicate_id_rejected(self):
        self.assert_invalid([self.events[0], copy.deepcopy(self.events[0])])

    def test_empty_input_rejected(self):
        self.assert_invalid([])

    def test_non_object_rejected(self):
        self.assert_invalid(["not an incident"])

    def test_missing_field_rejected(self):
        event = copy.deepcopy(self.events[0])
        del event["target_age_days"]
        self.assert_invalid([event])

    def test_ground_truth_field_rejected_in_input(self):
        self.assert_invalid(self.changed(expected_recoverable=True))

    def test_unknown_table_rejected(self):
        self.assert_invalid(self.changed(table_id="unknown_table"))

    def test_unknown_split_rejected(self):
        self.assert_invalid(self.changed(split="test"))

    def test_shift_scenario_rejected_in_development(self):
        self.assert_invalid(self.changed(scenario="S2_tail_shift"))

    def test_seed_must_belong_to_split(self):
        self.assert_invalid(self.changed(seed=2001))

    def test_boolean_seed_rejected(self):
        self.assert_invalid(self.changed(seed=True))

    def test_infrastructure_flag_requires_boolean(self):
        for flag in ["false", 0, 1, None]:
            with self.subTest(flag=flag):
                self.assert_invalid(self.changed(infrastructure_lost=flag))

    def test_negative_age_rejected(self):
        self.assert_invalid(self.changed(detect_delay_days=-1, target_age_days=-1))

    def test_nonfinite_age_rejected(self):
        for age in [math.nan, math.inf, -math.inf]:
            with self.subTest(age=age):
                self.assert_invalid(self.changed(detect_delay_days=age, target_age_days=age))

    def test_float64_overflow_age_rejected(self):
        self.assert_invalid(self.changed(detect_delay_days=10**1000, target_age_days=10**1000))

    def test_boolean_age_rejected(self):
        self.assert_invalid(self.changed(detect_delay_days=True, target_age_days=True))

    def test_age_sum_mismatch_rejected(self):
        self.assert_invalid(self.changed(target_age_days=10))

    def test_empty_id_rejected(self):
        self.assert_invalid(self.changed(incident_id=""))

    def test_id_metadata_mismatch_rejected(self):
        self.assert_invalid(self.changed(incident_id="development-S0_main-s1001-raw_ingest-0001"))

    def test_bom_and_blank_lines_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.jsonl"
            path.write_text("\n" + json.dumps(self.events[0]) + "\n\n", encoding="utf-8-sig")
            self.assertEqual(read_fixture(path, self.config), [self.events[0]])

    def test_bad_json_reports_line_number(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.jsonl"
            path.write_text(json.dumps(self.events[0]) + "\n{bad json}\n", encoding="utf-8")
            with self.assertRaisesRegex(FixtureValidationError, "line 2"):
                read_fixture(path, self.config)

    def test_expected_answers_are_hand_fixture_only(self):
        self.assertTrue(self.expected["fixture_only"])
        self.assertEqual(self.expected["source"], "hand_calculated")
        self.assertEqual(self.expected["budget_gb"], 810)
        labels = self.expected["incident_labels"]
        self.assertEqual(len(labels), 7)
        self.assertEqual(set(labels.values()), {e["incident_id"] for e in self.events})

    def test_expected_valid_policy_answers(self):
        profiles = self.config["profiles"]
        for name, policy in self.expected["policies"].items():
            if not policy["feasible"]:
                continue
            with self.subTest(policy=name):
                ttl = policy["ttl_days"]
                cost = sum(p["history_gb_per_day"] * ttl[p["table_id"]] for p in profiles)
                self.assertEqual(cost, policy["cost_gb"])
                self.assertLessEqual(cost, self.config["budget"]["main_gb"])
                self.assertTrue(all(ttl[p["table_id"]] >= p["min_ttl_days"] for p in profiles))
                # Independent oracle check; this is not a production evaluator.
                recovered = {e["incident_id"] for e in self.events if
                             not e["infrastructure_lost"] and e["target_age_days"] <= ttl[e["table_id"]]}
                self.assertEqual(recovered, set(policy["recoverable_incident_ids"]))
                self.assertEqual(len(recovered), policy["recoverable_count"])
                self.assertEqual(len(self.events), policy["total_count"])
                self.assertAlmostEqual(len(recovered) / len(self.events), policy["coverage"])
                logical = [e for e in self.events if not e["infrastructure_lost"]]
                self.assertEqual(len(logical), policy["logical_total_count"])
                self.assertAlmostEqual(len(recovered) / len(logical), policy["logical_only_coverage"])

    def test_expected_invalid_policy_answers(self):
        profiles = self.config["profiles"]
        for name, policy in self.expected["policies"].items():
            if policy["feasible"]:
                continue
            with self.subTest(policy=name):
                ttl = policy["ttl_days"]
                cost = sum(p["history_gb_per_day"] * ttl[p["table_id"]] for p in profiles)
                violations = []
                if cost > self.config["budget"]["main_gb"]:
                    violations.append("budget_violation")
                if any(ttl[p["table_id"]] < p["min_ttl_days"] for p in profiles):
                    violations.append("min_ttl_violation")
                self.assertEqual(cost, policy["cost_gb"])
                self.assertEqual(violations, policy["violations"])
                self.assertFalse(policy["coverage_claim_allowed"])
                self.assertNotIn("coverage", policy)

    def test_cli_success(self):
        result = subprocess.run([sys.executable, "-m", "src.fixture_contract"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["incident_count"], 7)
        self.assertTrue(data["fixture_only"])

    def test_cli_rejects_invalid_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.jsonl"
            path.write_text(json.dumps(self.changed(target_age_days=99)[0]), encoding="utf-8")
            result = subprocess.run([sys.executable, "-m", "src.fixture_contract", "--fixture", str(path)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("target_age_days", result.stderr)


if __name__ == "__main__":
    unittest.main()
