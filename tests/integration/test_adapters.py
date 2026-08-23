import unittest
import tempfile
from pathlib import Path

from quasar_engine.adapters.astronomy import (
    AstronomyAdapter,
    generate_synthetic_astronomy,
    load_nasa_lightcurve_csv,
)
from quasar_engine.adapters.fraud import (
    FraudAdapter,
    generate_synthetic_fraud,
    load_ieee_cis_transactions,
)


class AdapterTests(unittest.TestCase):
    def test_both_domains_emit_the_same_contract(self) -> None:
        fraud = FraudAdapter().adapt(generate_synthetic_fraud(100, 7)[0])
        astronomy = AstronomyAdapter().adapt(generate_synthetic_astronomy(100, 7)[0])
        self.assertEqual(fraud.context["domain"], "fraud")
        self.assertEqual(astronomy.context["domain"], "astronomy")
        self.assertTrue(fraud.features)
        self.assertTrue(astronomy.features)
        self.assertEqual(type(fraud), type(astronomy))

    def test_real_dataset_csv_paths_emit_common_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ieee = root / "ieee.csv"
            ieee.write_text(
                "TransactionID,TransactionDT,TransactionAmt,dist1,isFraud\n"
                "1,10,125.5,2.0,0\n2,20,900.0,,1\n",
                encoding="utf-8",
            )
            lightcurve = root / "lightcurve.csv"
            lightcurve.write_text(
                "time,flux,flux_err,label,curve_id\n"
                "0.0,1.0,0.01,0,K42\n0.5,0.92,0.02,1,K42\n",
                encoding="utf-8",
            )
            fraud = load_ieee_cis_transactions(ieee)
            astronomy = load_nasa_lightcurve_csv(lightcurve)
            self.assertEqual(len(fraud), 2)
            self.assertEqual(len(astronomy), 2)
            self.assertFalse(fraud[0].context["synthetic"])
            self.assertEqual(astronomy[1].target_future, 1)


if __name__ == "__main__":
    unittest.main()
