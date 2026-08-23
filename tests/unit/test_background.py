from datetime import datetime, timedelta, timezone
import unittest

from quasar_engine.core.background.statistical import StatisticalBackground
from quasar_engine.core.contract.observation import Observation


class StatisticalBackgroundTests(unittest.TestCase):
    def observation(self, index: int, value: float) -> Observation:
        return Observation(
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=index),
            source_id="sensor",
            features={"x": value},
        )

    def test_score_uses_only_prior_observations(self) -> None:
        model = StatisticalBackground(window=8, min_history=3)
        for index, value in enumerate((0.0, 0.1, -0.1)):
            model.update(self.observation(index, value))
        outlier = self.observation(3, 10.0)
        before_update = model.score(outlier)
        self.assertTrue(before_update.ready)
        self.assertGreater(before_update.residuals["x"], 10.0)
        self.assertEqual(before_update.sample_count, 3)
        model.update(outlier)
        self.assertEqual(model.score(self.observation(4, 0.0)).sample_count, 4)


if __name__ == "__main__":
    unittest.main()

