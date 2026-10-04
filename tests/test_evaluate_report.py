import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.evaluate import config_hash, evaluate_pair, recoverable
from src.report import write_report


ROOT = Path(__file__).resolve().parents[1]
HASH = "daa6825ef86ac612ff0bffed9e69ec69f6a7236e3ec079f174132513af022d4d"


def policy(policy_id, kind, ttl):
    return {
        "policy_id": policy_id,
        "kind": kind,
        "ttl_days": ttl,
        "budget_gb": 810,
        "cost_gb": 810 if kind == "baseline_uniform" else 760,
        "feasible": True,
        "config_hash": HASH,
        "locked_on_split": "development",
        "training_scenario": "S0_main",
        "development_seed": 1001,
        "locked_at": "2026-10-05T10:15:00+07:00",
    }


class EvaluateReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "configs/experiment.sample.json").read_text(encoding="utf-8"))
        cls.incidents = [
            json.loads(line)
            for line in (ROOT / "tests/fixtures/incidents.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        cls.baseline = policy(
            "baseline-S0_main-dev1001-B810", "baseline_uniform",
            {"raw_ingest": 30, "curated_business": 30, "training_dataset": 30},
        )
        cls.optimized = policy(
            "optimized-S0_main-dev1001-B810", "optimized_per_profile",
            {"raw_ingest": 14, "curated_business": 60, "training_dataset": 90},
        )

    def test_contract_hash_and_recovery_boundaries(self):
        self.assertEqual(config_hash(self.config), HASH)
        raw = [item for item in self.incidents if item["table_id"] == "raw_ingest"]
        ttl = {"raw_ingest": 1}
        self.assertEqual([recoverable(item, ttl) for item in raw], [True, True, False, False])

    def test_paired_metrics_cost_and_profiles(self):
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, self.optimized], "fixture-task-07-10"
        )
        baseline = metrics["policies"][self.baseline["policy_id"]]
        optimized = metrics["policies"][self.optimized["policy_id"]]
        self.assertEqual(metrics["status"], "valid")
        self.assertEqual((baseline["recoverable"], baseline["total"], baseline["cost_gb"]), (3, 6, 810))
        self.assertEqual((optimized["recoverable"], optimized["total"], optimized["cost_gb"]), (5, 6, 760))
        self.assertAlmostEqual(metrics["paired"]["delta_pp"], 100 / 3)
        self.assertEqual(baseline["coverage_by_profile"]["raw_ingest"], 0.75)
        self.assertEqual(optimized["coverage_infra_loss"], 0)

    def test_budget_and_minimum_violations_mark_run_invalid(self):
        over_budget = copy.deepcopy(self.optimized)
        over_budget["ttl_days"] = {name: 90 for name in over_budget["ttl_days"]}
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, over_budget], "fixture-invalid-budget"
        )
        result = metrics["policies"][over_budget["policy_id"]]
        self.assertEqual(metrics["status"], "invalid")
        self.assertEqual((result["cost_gb"], result["budget_violations"]), (2430, 1))
        self.assertIsNone(metrics["paired"]["delta_pp"])

        below_minimum = copy.deepcopy(self.optimized)
        below_minimum["ttl_days"]["training_dataset"] = 7
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, below_minimum], "fixture-invalid-minimum"
        )
        self.assertEqual(metrics["policies"][below_minimum["policy_id"]]["min_ttl_violations"], 1)

    def test_bad_policy_values_are_invalid_without_crashing(self):
        bad_type = copy.deepcopy(self.optimized)
        bad_type["ttl_days"]["raw_ingest"] = "14"
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, bad_type], "fixture-invalid-type"
        )
        reasons = metrics["policies"][bad_type["policy_id"]]["invalid_reasons"]
        self.assertEqual(metrics["status"], "invalid")
        self.assertTrue(any("TTL values" in reason for reason in reasons))

        duplicate = copy.deepcopy(self.optimized)
        duplicate["policy_id"] = self.baseline["policy_id"]
        with self.assertRaisesRegex(ValueError, "policy_id values must be unique"):
            evaluate_pair(
                self.config, self.incidents, [self.baseline, duplicate], "duplicate-policy"
            )

    def test_bad_age_equation_is_rejected(self):
        incidents = copy.deepcopy(self.incidents)
        incidents[0]["target_age_days"] = 9
        with self.assertRaisesRegex(ValueError, "H != A \\+ D \\+ L"):
            evaluate_pair(self.config, incidents, [self.baseline, self.optimized], "bad-input")

    def test_report_is_offline_and_never_overwrites(self):
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, self.optimized], "fixture-task-07-10"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unsafe = copy.deepcopy(metrics)
            unsafe["run_id"] = ".."
            with self.assertRaisesRegex(ValueError, "safe"):
                write_report(unsafe, root)
            report = write_report(metrics, root)
            page = report.read_text(encoding="utf-8")
            self.assertIn("fixture-task-07-10", page)
            self.assertIn("FIXTURE DATA - NOT EXPERIMENT RESULTS", page)
            self.assertIn("Ch\u01b0a c\u00f3 nh\u1eadn x\u00e9t LLM", page)
            self.assertTrue((report.parent / "metrics.json").exists())
            self.assertTrue((report.parent / "results.csv").exists())
            with self.assertRaises(FileExistsError):
                write_report(metrics, root)


if __name__ == "__main__":
    unittest.main()
