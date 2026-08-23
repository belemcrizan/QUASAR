import unittest

from quasar_engine.core.background.base import BackgroundSnapshot
from quasar_engine.core.dynamics.factory import DynamicalEvidence
from quasar_engine.core.emergence.detector import EmergenceDetector


class EmergenceTests(unittest.TestCase):
    def test_convergent_evidence_creates_candidate(self) -> None:
        detector = EmergenceDetector(
            {
                "residual": 0.30,
                "entropy_change": 0.10,
                "mutual_info_change": 0.12,
                "js_divergence": 0.20,
                "change_point": 0.18,
                "regime_change": 0.10,
            },
            threshold=0.34,
        )
        snapshot = BackgroundSnapshot(
            residuals={"a": 3.0, "b": 2.5, "c": 2.0},
            centers={},
            scales={},
            sample_count=30,
            ready=True,
        )
        dynamics = DynamicalEvidence(0.4, 0.4, 0.6, 0.5, 0.4)
        result = detector.evaluate(snapshot, dynamics)
        self.assertTrue(result.is_candidate)
        self.assertGreaterEqual(result.score, detector.threshold)
        self.assertEqual(len(result.evidence), 6)


if __name__ == "__main__":
    unittest.main()

