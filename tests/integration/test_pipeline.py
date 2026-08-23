import tempfile
import unittest
from pathlib import Path

from quasar_engine.adapters.fraud import FraudAdapter, generate_synthetic_fraud
from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline
from quasar_engine.experiment import run_domain


class PipelineTests(unittest.TestCase):
    def test_labels_cannot_change_predictions(self) -> None:
        observations = FraudAdapter().adapt_many(generate_synthetic_fraud(140, 9))
        inverted = [
            item.model_copy(update={"target_future": 1 - int(item.target_future or 0)})
            for item in observations
        ]
        first = DiscoveryPipeline(PipelineConfig()).process(observations)
        second = DiscoveryPipeline(PipelineConfig()).process(inverted)
        self.assertEqual(
            [item.forecast.probability for item in first.scored],
            [item.forecast.probability for item in second.scored],
        )

    def test_both_registered_experiments_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for domain in ("fraud", "astronomy"):
                result = run_domain(domain, points=180, seed=42, output_dir=Path(directory) / domain)
                self.assertGreater(result["candidates"], 0)
                self.assertIn("calibrated_test", result["metrics"])
                self.assertTrue((Path(directory) / domain / "results.json").exists())
                self.assertTrue((Path(directory) / domain / "report.md").exists())
                self.assertIn("isolation_forest", result["metrics"]["baselines_test"])


if __name__ == "__main__":
    unittest.main()
