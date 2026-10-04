import copy
import csv
import json
import subprocess
import sys
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

    def test_invalid_policy_does_not_publish_zero_metrics(self):
        outside_grid = copy.deepcopy(self.optimized)
        outside_grid["ttl_days"]["raw_ingest"] = 13
        outside_grid["cost_gb"] = 740
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, outside_grid], "outside-grid"
        )
        result = metrics["policies"][outside_grid["policy_id"]]
        self.assertEqual((metrics["status"], result["grid_violations"]), ("invalid", 1))
        self.assertIsNone(result["coverage_total"])
        self.assertIsNone(result["recoverable"])

        nonfinite = copy.deepcopy(self.optimized)
        nonfinite["ttl_days"]["raw_ingest"] = float("nan")
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, nonfinite], "nonfinite"
        )
        result = metrics["policies"][nonfinite["policy_id"]]
        self.assertIsNone(result["coverage_total"])
        self.assertTrue(any("finite" in reason for reason in result["invalid_reasons"]))

    def test_routing_and_paired_budget_are_validated(self):
        wrong_seed = copy.deepcopy(self.optimized)
        wrong_seed["development_seed"] = 1002
        with self.assertRaisesRegex(ValueError, "development_seed mismatch"):
            evaluate_pair(
                self.config, self.incidents, [self.baseline, wrong_seed], "wrong-route"
            )

        different_budget = copy.deepcopy(self.optimized)
        different_budget["budget_gb"] = 1200
        metrics = evaluate_pair(
            self.config, self.incidents, [self.baseline, different_budget], "budget-mismatch"
        )
        self.assertEqual(metrics["status"], "invalid")
        for result in metrics["policies"].values():
            self.assertIn("policies must use the same budget_gb", result["invalid_reasons"])

        undeclared_baseline = copy.deepcopy(self.baseline)
        undeclared_optimized = copy.deepcopy(self.optimized)
        for item in (undeclared_baseline, undeclared_optimized):
            item["budget_gb"] = 999
        metrics = evaluate_pair(
            self.config,
            self.incidents,
            [undeclared_baseline, undeclared_optimized],
            "undeclared-budget",
        )
        self.assertEqual(metrics["status"], "invalid")
        for result in metrics["policies"].values():
            self.assertIn("policy budget_gb is not declared in config", result["invalid_reasons"])

    def test_cli_writes_invalid_artifact_for_bad_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad_config = root / "bad-config.json"
            output = root / "metrics.json"
            bad_config.write_text("{", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.evaluate",
                    "--config",
                    str(bad_config),
                    "--incidents",
                    str(ROOT / "tests/fixtures/incidents.jsonl"),
                    "--policy",
                    str(ROOT / "tests/fixtures/baseline_policy.json"),
                    "--policy",
                    str(ROOT / "tests/fixtures/optimized_policy.json"),
                    "--run-id",
                    "bad-config",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            artifact = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(artifact["status"], "invalid")
            self.assertIsNone(artifact["config_hash"])

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

            wrong_commentary = copy.deepcopy(metrics)
            wrong_commentary["run_id"] = "wrong-commentary"
            with self.assertRaisesRegex(ValueError, "run_id"):
                write_report(
                    wrong_commentary,
                    root,
                    {"status": "success", "response": "ok", "run_id": "another-run"},
                )
            self.assertFalse((root / "wrong-commentary").exists())

            wrong_config_metrics = copy.deepcopy(metrics)
            wrong_config_metrics["run_id"] = "wrong-config"
            wrong_config = copy.deepcopy(self.config)
            wrong_config["budget"]["main_gb"] = 811
            with self.assertRaisesRegex(ValueError, "config hash"):
                write_report(wrong_config_metrics, root, config=wrong_config)
            self.assertFalse((root / "wrong-config").exists())

            report = write_report(metrics, root, config=self.config)
            page = report.read_text(encoding="utf-8")
            self.assertIn("fixture-task-07-10", page)
            self.assertIn("FIXTURE DATA - NOT EXPERIMENT RESULTS", page)
            self.assertIn("Ch\u01b0a c\u00f3 nh\u1eadn x\u00e9t LLM", page)
            self.assertIn("config.json", page)
            self.assertTrue((report.parent / "metrics.json").exists())
            self.assertTrue((report.parent / "config.json").exists())
            with (report.parent / "results.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 2)
            self.assertIn("coverage_logical_only", rows[0])
            self.assertIn("grid_violations", rows[0])
            with self.assertRaises(FileExistsError):
                write_report(metrics, root, config=self.config)


if __name__ == "__main__":
    unittest.main()
