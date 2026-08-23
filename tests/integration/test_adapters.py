import unittest

from quasar_engine.adapters.astronomy import AstronomyAdapter, generate_synthetic_astronomy
from quasar_engine.adapters.fraud import FraudAdapter, generate_synthetic_fraud


class AdapterTests(unittest.TestCase):
    def test_both_domains_emit_the_same_contract(self) -> None:
        fraud = FraudAdapter().adapt(generate_synthetic_fraud(100, 7)[0])
        astronomy = AstronomyAdapter().adapt(generate_synthetic_astronomy(100, 7)[0])
        self.assertEqual(fraud.context["domain"], "fraud")
        self.assertEqual(astronomy.context["domain"], "astronomy")
        self.assertTrue(fraud.features)
        self.assertTrue(astronomy.features)
        self.assertEqual(type(fraud), type(astronomy))


if __name__ == "__main__":
    unittest.main()

