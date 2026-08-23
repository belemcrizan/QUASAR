"""Protocol adapter for optional ML background models.

The POC deliberately has no LightGBM/XGBoost dependency. A future model only
needs to implement ``BackgroundModel`` and register itself.
"""

from quasar_engine.core.background.base import BackgroundModel

__all__ = ["BackgroundModel"]

