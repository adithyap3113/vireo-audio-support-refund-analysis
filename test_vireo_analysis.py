import unittest
from pathlib import Path
from vireo_analysis import run_analysis

class TestVireoAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = run_analysis()
        cls.h = cls.r["headline"]

    def test_dedupe_and_currency_reconcile(self):
        self.assertEqual(self.h["raw_rows"], 12238)
        self.assertEqual(self.h["unique_tickets"], 11600)
        self.assertEqual(self.h["duplicate_ticket_ids"], 638)
        self.assertEqual(self.h["duplicate_amount_mismatches"], 0)
        self.assertAlmostEqual(self.h["normalized_refund_sum"], 6709932.0, places=2)

    def test_q3_baseline(self):
        self.assertAlmostEqual(self.h["baseline_refund_rate"], 0.2197504069, places=6)

    def test_policy_exception_counts(self):
        self.assertEqual(self.h["double_award_tickets"], 166)
        self.assertAlmostEqual(self.h["double_award_total_exposure_inr"], 871161.0, places=2)

    def test_model_agreement(self):
        self.assertGreater(self.h["ai_standard_reason_agreement"], 0.85)

if __name__ == "__main__":
    unittest.main()
