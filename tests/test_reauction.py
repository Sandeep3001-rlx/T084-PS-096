import sys
import unittest
from pathlib import Path
from decimal import Decimal
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reauction import calculate_reauction_floor, next_auction_date


class TestReauction(unittest.TestCase):

    def test_initial_floor(self):
        self.assertEqual(
            calculate_reauction_floor("2500", 0),
            Decimal("2250.00")
        )

    def test_first_reauction_floor(self):
        self.assertEqual(
            calculate_reauction_floor("2500", 1),
            Decimal("2200.00")
        )

    def test_floor_decreases_each_attempt(self):
        first = calculate_reauction_floor("2500", 1)
        second = calculate_reauction_floor("2500", 2)
        self.assertGreater(first, second)

    def test_floor_never_falls_below_80_percent(self):
        self.assertEqual(
            calculate_reauction_floor("2500", 100),
            Decimal("2000.00")
        )

    def test_zero_reference_price_rejected(self):
        with self.assertRaises(ValueError):
            calculate_reauction_floor("0", 0)

    def test_negative_reauction_number_rejected(self):
        with self.assertRaises(ValueError):
            calculate_reauction_floor("2500", -1)

    def test_next_auction_is_next_day(self):
        unsold_date = date(2026, 10, 19)
        self.assertEqual(
            next_auction_date(unsold_date),
            unsold_date + timedelta(days=1)
        )


if __name__ == "__main__":
    unittest.main()