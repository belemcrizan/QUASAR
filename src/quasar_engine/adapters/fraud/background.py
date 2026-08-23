"""Documented fraud priors for future experiments.

The first POC does not inject these priors into the core; keeping the background
domain-neutral is part of the horizontal-generalization test.
"""

DEFAULT_FEATURES = ("amount_log", "velocity", "counterparty_risk", "network_density")

