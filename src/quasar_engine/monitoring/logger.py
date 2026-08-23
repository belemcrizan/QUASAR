"""Minimal structured logging."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any


def configure_logging(level: str | None = None) -> None:
    logging.basicConfig(
        level=(level or os.getenv("QUASAR_LOG_LEVEL", "INFO")).upper(),
        format="%(levelname)s %(name)s %(message)s",
    )


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    payload = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), **fields}
    logger.info(json.dumps(payload, sort_keys=True, default=str))

