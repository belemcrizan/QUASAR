import unittest

import numpy as np

from quasar_engine.core.validation.baselines import IsolationForestBaseline


class BaselineTests(unittest.TestCase):
    def test_isolation_forest_scores_clear_outlier_higher(self) -> None:
        rng = np.random.default_rng(7)
        normal = rng.normal(0.0, 0.2, size=(100, 3))
        outlier = np.asarray([[6.0, 6.0, 6.0]])
        model = IsolationForestBaseline(n_estimators=48, sample_size=64, seed=7).fit(normal)
        scores = model.score_samples(np.vstack([normal[:10], outlier]))
        self.assertGreater(scores[-1], max(scores[:-1]))


if __name__ == "__main__":
    unittest.main()

