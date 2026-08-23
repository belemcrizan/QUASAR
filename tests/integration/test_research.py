import tempfile
import unittest
from pathlib import Path

from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.research import run_multiseed, run_scalability_study


class ResearchStudyTests(unittest.TestCase):
    def test_multiseed_and_scale_reports_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            multi = run_multiseed(["fraud"], [3, 4], 120, PipelineConfig(), root / "multi")
            self.assertEqual(multi["seed_count"], 2)
            self.assertTrue((root / "multi" / "report.md").exists())
            scale = run_scalability_study(
                "fraud", [100], 1, 3, PipelineConfig(), root / "scale"
            )
            self.assertEqual(scale["sizes"][0]["observations"], 100)
            self.assertTrue((root / "scale" / "report.md").exists())


if __name__ == "__main__":
    unittest.main()

