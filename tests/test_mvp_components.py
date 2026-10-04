"""Hand answers and integration checks for TASK-04/05/06."""
import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.config import config_hash, load_config
from src.cost_model import check_policy, history_cost_gb, minimum_required_cost_gb
from src.evaluate import evaluate_policy
from src.fixture_contract import read_fixture
from src.generator import generate_incidents, incidents_jsonl, summarize_incidents
from src.policies import uniform_baseline

ROOT = Path(__file__).resolve().parents[1]


class MVPComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config(ROOT / "configs/experiment.sample.json")

    def ttl(self, values):
        return dict(zip([p["table_id"] for p in self.config["profiles"]], values))

    def test_hand_costs(self):
        for vector, cost in [((1, 7, 14), 83), ((14, 60, 90), 760),
                             ((30, 30, 30), 810), ((90, 90, 90), 2430)]:
            with self.subTest(vector=vector):
                self.assertEqual(history_cost_gb(self.ttl(vector), self.config["profiles"]), cost)
        self.assertEqual(minimum_required_cost_gb(self.config), 83)

    def test_invalid_policy_reasons(self):
        for vector, code in [((90, 90, 90), "budget_violation"),
                             ((1, 7, 7), "min_ttl_violation"), ((2, 7, 14), "ttl_grid_violation")]:
            with self.subTest(vector=vector):
                result = check_policy(self.ttl(vector), self.config)
                self.assertFalse(result["coverage_claim_allowed"])
                self.assertIn(code, [x["code"] for x in result["violations"]])

    def test_bad_ttl_mappings(self):
        for value in [None, {}, {"extra": 1}, self.ttl((-1, 7, 14)),
                      self.ttl((True, 7, 14)), self.ttl((math.nan, 7, 14)),
                      self.ttl((math.inf, 7, 14)), self.ttl((10**1000, 7, 14))]:
            with self.subTest(value=str(value)[:50]):
                result = check_policy(value, self.config)
                self.assertFalse(result["feasible"])
                self.assertIsNone(result["cost_gb"])

    def test_budget_below_minimum(self):
        result = check_policy(self.ttl((1, 7, 14)), self.config, 82)
        self.assertFalse(result["any_grid_policy_feasible"])
        self.assertFalse(result["feasible"])

    def test_baseline_hand_answers(self):
        for budget, ttl, cost in [(450, 14, 378), (600, 14, 378), (810, 30, 810),
                                  (1200, 30, 810), (1620, 60, 1620)]:
            with self.subTest(budget=budget):
                policy = uniform_baseline(self.config, budget)
                self.assertTrue(policy["feasible"])
                self.assertEqual(set(policy["ttl_days"].values()), {ttl})
                self.assertEqual(policy["cost_gb"], cost)

    def test_uniform_infeasible_is_distinct_from_any_policy_feasible(self):
        baseline = uniform_baseline(self.config, 300)
        self.assertFalse(baseline["feasible"])
        self.assertEqual(baseline["status"], "infeasible")
        self.assertIsNone(baseline["cost_gb"])
        self.assertTrue(check_policy(self.ttl((1, 7, 14)), self.config, 300)["feasible"])

    def test_baseline_development_metadata_only(self):
        for args in [dict(development_seed=2001), dict(development_seed=True),
                     dict(training_scenario="S2_tail_shift"), dict(locked_at="2026-10-04T10:00:00Z")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                uniform_baseline(self.config, **args)

    def test_hash_matches_contract_and_excludes_notes(self):
        self.assertEqual(config_hash(self.config),
                         "daa6825ef86ac612ff0bffed9e69ec69f6a7236e3ec079f174132513af022d4d")
        changed = copy.deepcopy(self.config)
        changed["meta"].update(status="draft", note="different note")
        self.assertEqual(config_hash(changed), config_hash(self.config))
        changed["budget"]["main_gb"] = 800
        self.assertNotEqual(config_hash(changed), config_hash(self.config))

    def test_seed_reproducibility_and_split_separation(self):
        dev = generate_incidents(self.config, "development", "S0_main", 1001)
        repeat = generate_incidents(self.config, "development", "S0_main", 1001)
        holdout = generate_incidents(self.config, "holdout", "S0_main", 2001)
        self.assertEqual(incidents_jsonl(dev), incidents_jsonl(repeat))
        self.assertEqual(len(dev), 900)
        self.assertEqual(len(holdout), 900)
        self.assertFalse(set(e["incident_id"] for e in dev) & set(e["incident_id"] for e in holdout))
        self.assertNotEqual([e["detect_delay_days"] for e in dev],
                            [e["detect_delay_days"] for e in holdout])

    def test_s0_and_s1_counts_and_delay_bounds(self):
        for split, seed in [("development", 1001), ("holdout", 2001)]:
            for scenario, lost_count in [("S0_main", 0), ("S1_infra_loss", 24)]:
                with self.subTest(split=split, scenario=scenario):
                    events = generate_incidents(self.config, split, scenario, seed)
                    summary = summarize_incidents(events, self.config)
                    for profile in self.config["profiles"]:
                        table = profile["table_id"]
                        stats = summary["profiles"][table]
                        self.assertEqual(stats["count"], 300)
                        self.assertEqual(stats["infrastructure_lost"], lost_count)
                        bounds = profile["detect_delay_days"]["components"]
                        subset = [e for e in events if e["table_id"] == table]
                        self.assertTrue(all(any(c["low"] <= e["detect_delay_days"] < c["high"]
                                                for c in bounds) for e in subset))
                        self.assertTrue(all(e["target_age_days"] == e["detect_delay_days"] for e in subset))

    def test_invalid_requests_and_config_fail_fast(self):
        for split, scenario, seed in [("holdout", "S0_main", 1001),
                                      ("development", "S2_tail_shift", 1001),
                                      ("development", "S0_main", True)]:
            with self.subTest(split=split, scenario=scenario, seed=seed), self.assertRaises(ValueError):
                generate_incidents(self.config, split, scenario, seed)
        bad = copy.deepcopy(self.config)
        bad["scenarios"][0]["overrides"]["unknown.override"] = {"dist": "constant", "value": 1}
        with self.assertRaises(ValueError):
            generate_incidents(bad, "development", "S0_main", 1001)

    def test_existing_evaluator_matches_fixture_oracle(self):
        events = read_fixture(ROOT / "tests/fixtures/incidents.sample.jsonl", self.config)
        expected = json.loads((ROOT / "tests/fixtures/expected.sample.json").read_text(encoding="utf-8"))
        for sample in expected["policies"].values():
            if not sample["feasible"]:
                continue
            policy = dict(sample, budget_gb=810)
            result = evaluate_policy(self.config, policy, events)
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["metrics"]["cost_gb"], sample["cost_gb"])
            self.assertEqual(result["metrics"]["recoverable"], sample["recoverable_count"])
            self.assertAlmostEqual(result["metrics"]["coverage_total"], sample["coverage"])

    def test_generator_cli_preserves_old_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "dataset"
            command = [sys.executable, "-m", "src.generator", "--output-dir", str(directory)]
            first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            manifest = (directory / "manifest.json").read_bytes()
            second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(second.returncode, 2)
            self.assertEqual((directory / "manifest.json").read_bytes(), manifest)


if __name__ == "__main__":
    unittest.main()
