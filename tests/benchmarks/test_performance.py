import os
import time
import unittest

from quasar_engine.adapters.fraud import FraudAdapter, generate_synthetic_fraud
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline


@unittest.skipUnless(os.getenv("RUN_QUASAR_BENCHMARKS") == "1", "opt-in benchmark")
class PerformanceBenchmark(unittest.TestCase):
    def test_one_thousand_observations(self) -> None:
        observations = FraudAdapter().adapt_many(generate_synthetic_fraud(1_000, 42))
        started = time.perf_counter()
        DiscoveryPipeline().process(observations)
        elapsed = time.perf_counter() - started
        self.assertLess(elapsed, 30.0)


if __name__ == "__main__":
    unittest.main()

