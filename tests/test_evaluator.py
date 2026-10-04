import unittest
from src.evaluate import evaluate_policy

class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.config = {
            "profiles": [
                {"table_id": "raw_ingest", "history_gb_per_day": 20, "min_ttl_days": 1},
                {"table_id": "curated_business", "history_gb_per_day": 5, "min_ttl_days": 7}
            ]
        }
        self.policy = {
            "policy_id": "test_policy",
            "feasible": True,
            "budget_gb": 810,
            "ttl_days": {
                "raw_ingest": 10,
                "curated_business": 10
            }
        }
        # Cost = 20*10 + 5*10 = 250 <= 810

    def test_h_less_than_ttl(self):
        # H = 5 < TTL = 10 -> recoverable
        incidents = [
            {
                "incident_id": "inc_1",
                "table_id": "raw_ingest",
                "anchor_gap_days": 2,
                "detect_delay_days": 2,
                "response_lag_days": 1,
                "target_age_days": 5,
                "infrastructure_lost": False
            }
        ]
        res = evaluate_policy(self.config, self.policy, incidents)
        self.assertEqual(res["status"], "valid")
        self.assertEqual(res["metrics"]["recoverable"], 1)

    def test_h_equal_ttl(self):
        # H = 10 == TTL = 10 -> recoverable (boundary inclusive)
        incidents = [
            {
                "incident_id": "inc_2",
                "table_id": "raw_ingest",
                "anchor_gap_days": 5,
                "detect_delay_days": 5,
                "response_lag_days": 0,
                "target_age_days": 10,
                "infrastructure_lost": False
            }
        ]
        res = evaluate_policy(self.config, self.policy, incidents)
        self.assertEqual(res["status"], "valid")
        self.assertEqual(res["metrics"]["recoverable"], 1)

    def test_h_greater_than_ttl(self):
        # H = 11 > TTL = 10 -> unrecoverable
        incidents = [
            {
                "incident_id": "inc_3",
                "table_id": "raw_ingest",
                "anchor_gap_days": 5,
                "detect_delay_days": 5,
                "response_lag_days": 1,
                "target_age_days": 11,
                "infrastructure_lost": False
            }
        ]
        res = evaluate_policy(self.config, self.policy, incidents)
        self.assertEqual(res["status"], "valid")
        self.assertEqual(res["metrics"]["recoverable"], 0)

    def test_infrastructure_lost(self):
        # H = 5 < TTL = 10 but infra lost -> unrecoverable
        incidents = [
            {
                "incident_id": "inc_4",
                "table_id": "raw_ingest",
                "anchor_gap_days": 2,
                "detect_delay_days": 2,
                "response_lag_days": 1,
                "target_age_days": 5,
                "infrastructure_lost": True
            }
        ]
        res = evaluate_policy(self.config, self.policy, incidents)
        self.assertEqual(res["status"], "valid")
        self.assertEqual(res["metrics"]["recoverable"], 0)
        self.assertEqual(res["metrics"]["coverage_total"], 0.0)

    def test_budget_violation(self):
        # Change policy to exceed budget
        policy_invalid = {
            "policy_id": "test_policy_budget",
            "feasible": True,
            "budget_gb": 100,
            "ttl_days": {
                "raw_ingest": 10, # cost = 20*10 = 200 > 100
                "curated_business": 10
            }
        }
        incidents = []
        res = evaluate_policy(self.config, policy_invalid, incidents)
        self.assertEqual(res["status"], "invalid")
        self.assertGreater(res["metrics"]["budget_violations"], 0)
        
    def test_input_validation(self):
        # H != A + D + L -> ValueError
        incidents = [
            {
                "incident_id": "inc_err",
                "table_id": "raw_ingest",
                "anchor_gap_days": 2,
                "detect_delay_days": 2,
                "response_lag_days": 2,
                "target_age_days": 10, # H is 10 instead of 6
                "infrastructure_lost": False
            }
        ]
        with self.assertRaises(ValueError):
            evaluate_policy(self.config, self.policy, incidents)

if __name__ == '__main__':
    unittest.main()
