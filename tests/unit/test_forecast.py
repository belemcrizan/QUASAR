import unittest

from quasar_engine.core.forecast.probabilistic import EnsembleEmergenceForecaster


class ForecastTests(unittest.TestCase):
    def test_ensemble_is_bounded_and_monotonic(self) -> None:
        model = EnsembleEmergenceForecaster(0.34, (5.0, 9.0, 15.0))
        values = [model.predict_probability(score) for score in (0.1, 0.34, 0.8)]
        self.assertEqual(values, sorted(values))
        self.assertAlmostEqual(values[1], 0.5)


if __name__ == "__main__":
    unittest.main()

