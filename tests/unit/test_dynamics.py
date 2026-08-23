import unittest

import numpy as np

from quasar_engine.core.dynamics.change_point import StandardizedMeanShift
from quasar_engine.core.dynamics.divergence import JensenShannonChange
from quasar_engine.core.dynamics.entropy import EntropyChange
from quasar_engine.core.dynamics.mutual_info import mutual_information_change


class DynamicsTests(unittest.TestCase):
    def test_all_normalized_metrics_are_bounded(self) -> None:
        reference = np.asarray([0.0, 0.1, -0.1, 0.05, -0.05, 0.02, 0.01, -0.02])
        recent = np.asarray([0.8, 1.0, 0.9, 1.1, 0.7, 1.2, 0.95, 1.05])
        scores = [
            EntropyChange().compare(reference, recent),
            JensenShannonChange().compare(reference, recent),
            StandardizedMeanShift().compare(reference, recent),
            mutual_information_change(reference, reference, recent, recent),
        ]
        for score in scores:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
        self.assertGreater(scores[1], 0.5)


if __name__ == "__main__":
    unittest.main()

