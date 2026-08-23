from pathlib import Path

from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.experiment import run_domain


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    run_domain(
        "fraud",
        points=360,
        seed=42,
        config=PipelineConfig.from_yaml(here.parents[1] / "configs" / "base.yaml"),
        output_dir=here,
    )

