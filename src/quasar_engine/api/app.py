"""Optional FastAPI surface; the local CLI remains the primary POC interface."""

from __future__ import annotations

from typing import Any

from quasar_engine import __version__
from quasar_engine.api.dependencies import new_pipeline
from quasar_engine.api.schemas import DetectRequest, DetectResponse


def create_app() -> Any:
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError(
            'API dependencies are optional. Install with: python -m pip install -e ".[api]"'
        ) from exc

    app = FastAPI(
        title="QUASAR Discovery Engine",
        version=__version__,
        description="Research POC API. No production or causal claims.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.post("/detect", response_model=DetectResponse)
    def detect(request: DetectRequest) -> DetectResponse:
        output = new_pipeline().process(request.observations)
        return DetectResponse(
            candidates=list(output.candidates),
            forecasts=[item.forecast for item in output.scored],
            hypotheses=list(output.hypotheses),
            scored_observations=len(output.scored),
        )

    return app

