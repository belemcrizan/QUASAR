import unittest

from quasar_engine.core.forecast.calibration import TemperatureCalibrator
from quasar_engine.core.forecast.conformal import SplitConformalInterval
from quasar_engine.core.validation.metrics import empirical_coverage, probabilistic_metrics


class MetricTests(unittest.TestCase):
    def test_perfect_predictions_have_zero_brier(self) -> None:
        metrics = probabilistic_metrics([0.0, 1.0, 0.0, 1.0], [0, 1, 0, 1])
        self.assertEqual(metrics["brier"], 0.0)
        self.assertEqual(metrics["auroc"], 1.0)

    def test_calibration_and_conformal_are_fitted(self) -> None:
        probabilities = [0.1, 0.2, 0.7, 0.8, 0.6, 0.3]
        labels = [0, 0, 1, 1, 1, 0]
        calibrated = TemperatureCalibrator().fit(probabilities, labels).transform(probabilities)
        conformal = SplitConformalInterval(0.8).fit(calibrated, labels)
        intervals = [conformal.interval(value) for value in calibrated]
        self.assertGreaterEqual(empirical_coverage(intervals, labels), 0.8)


if __name__ == "__main__":
    unittest.main()

