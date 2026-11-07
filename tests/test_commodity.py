import sys
import unittest
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from commodity import Commodity


class TestCommodity(unittest.TestCase):

    def test_commodity_registration_below_3000(self):
        wheat = Commodity("C001", "Wheat", "2500")
        self.assertEqual(wheat.commodity_id, "C001")
        self.assertEqual(wheat.name, "Wheat")
        self.assertEqual(wheat.msp, Decimal("2500"))
        # Default increment for MSP < 3000 is 5
        self.assertEqual(wheat.bidding_increment, Decimal("5"))

    def test_commodity_registration_at_or_above_3000(self):
        rice = Commodity("C002", "Basmati Rice", "3000")
        self.assertEqual(rice.msp, Decimal("3000"))
        # Default increment for MSP >= 3000 is 10
        self.assertEqual(rice.bidding_increment, Decimal("10"))

        cotton = Commodity("C003", "Cotton", "6500")
        self.assertEqual(cotton.bidding_increment, Decimal("10"))

    def test_commodity_custom_increment(self):
        special = Commodity("C004", "Special Pulse", "2800", bidding_increment="15")
        self.assertEqual(special.bidding_increment, Decimal("15"))

    def test_empty_id_rejected(self):
        with self.assertRaises(ValueError):
            Commodity("", "Wheat", "2500")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            Commodity("C001", "", "2500")

    def test_negative_msp_rejected(self):
        with self.assertRaises(ValueError):
            Commodity("C001", "Wheat", "-100")

    def test_zero_msp_rejected(self):
        with self.assertRaises(ValueError):
            Commodity("C001", "Wheat", "0")

    def test_negative_increment_rejected(self):
        with self.assertRaises(ValueError):
            Commodity("C001", "Wheat", "2500", bidding_increment="-5")


if __name__ == "__main__":
    unittest.main()
