from datetime import datetime
import math
import unittest

from pydantic import ValidationError

from quasar_engine.core.contract.observation import Observation


class ObservationContractTests(unittest.TestCase):
    def test_naive_timestamp_is_normalized_to_utc(self) -> None:
        observation = Observation(
            timestamp=datetime(2026, 1, 1),
            source_id="source",
            features={"value": 1.0},
        )
        self.assertIsNotNone(observation.timestamp.tzinfo)
        self.assertEqual(len(observation.observation_id), 20)

    def test_non_finite_feature_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Observation(
                timestamp=datetime(2026, 1, 1),
                source_id="source",
                features={"value": math.nan},
            )

    def test_unknown_fields_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            Observation.model_validate(
                {
                    "timestamp": "2026-01-01T00:00:00Z",
                    "source_id": "source",
                    "features": {"value": 1.0},
                    "unexpected": True,
                }
            )


if __name__ == "__main__":
    unittest.main()

