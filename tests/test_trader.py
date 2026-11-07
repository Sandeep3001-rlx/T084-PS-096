import sys
import unittest
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trader import Trader


class TestTrader(unittest.TestCase):

    def test_credit_limit(self):
        trader = Trader("T1", "Trader One", "10000")
        self.assertEqual(trader.credit_limit, Decimal("100000"))

    def test_bid_within_credit_limit(self):
        trader = Trader("T1", "Trader One", "10000")
        self.assertTrue(trader.can_bid("50000"))

    def test_bid_exactly_reaching_credit_limit(self):
        # Edge case 11: A trader reaching credit limit exactly
        trader = Trader("T1", "Trader One", "10000")
        self.assertTrue(trader.can_bid("100000"))

    def test_bid_exceeding_credit_limit(self):
        trader = Trader("T1", "Trader One", "10000")
        self.assertFalse(trader.can_bid("100001"))

    def test_winning_bid_increases_exposure(self):
        trader = Trader("T1", "Trader One", "10000")
        trader.place_bid("L1", "50000")
        self.assertEqual(trader.current_exposure(), Decimal("50000"))

    def test_losing_lot_removes_exposure(self):
        trader = Trader("T1", "Trader One", "10000")
        trader.place_bid("L1", "50000")
        trader.lose_lot("L1")
        self.assertEqual(trader.current_exposure(), Decimal("0"))

    def test_record_due(self):
        trader = Trader("T1", "Trader One", "10000")
        trader.record_due("L1", "20000")
        self.assertEqual(trader.outstanding_dues, Decimal("20000"))

    def test_make_payment(self):
        trader = Trader("T1", "Trader One", "10000")
        trader.record_due("L1", "20000")
        trader.make_payment("5000")
        self.assertEqual(trader.outstanding_dues, Decimal("15000"))

    def test_suspended_trader_cannot_bid(self):
        trader = Trader("T1", "Trader One", "10000")
        trader.suspended = True
        self.assertFalse(trader.can_bid("1000"))
        eligible, reason = trader.check_eligibility("1000")
        self.assertFalse(eligible)
        self.assertIn("suspended", reason)

    def test_negative_security_deposit_rejected(self):
        with self.assertRaises(ValueError):
            Trader("T1", "Trader One", "-100")

    def test_overdue_trader_cannot_bid(self):
        trader = Trader("T1", "Trader One", "10000")
        trader.overdue_days = 8
        self.assertFalse(trader.can_bid("1000"))
        eligible, reason = trader.check_eligibility("1000")
        self.assertFalse(eligible)
        self.assertIn("overdue", reason)

    def test_trader_empty_id_rejected(self):
        with self.assertRaises(ValueError):
            Trader("", "Trader One", "10000")

    def test_trader_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            Trader("T1", "", "10000")


if __name__ == "__main__":
    unittest.main()
