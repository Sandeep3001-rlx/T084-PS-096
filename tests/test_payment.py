import sys
import unittest
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payment import Payment


class TestPayment(unittest.TestCase):

    def setUp(self):
        self.created_at = datetime(2026, 10, 19, 10, 0, 0)
        self.payment = Payment(
            "L001", "T001", "100000", self.created_at
        )

    def test_initial_status(self):
        self.assertEqual(self.payment.status, "PENDING")

    def test_deadline_is_24_hours(self):
        self.assertEqual(
            self.payment.deadline,
            self.created_at + timedelta(hours=24)
        )

    def test_full_payment(self):
        self.payment.record_payment(
            "100000", self.created_at + timedelta(hours=12)
        )
        self.assertEqual(self.payment.status, "PAID")

    def test_partial_payment(self):
        self.payment.record_payment(
            "40000", self.created_at + timedelta(hours=12)
        )
        self.assertEqual(self.payment.status, "PARTIALLY_PAID")
        self.assertEqual(self.payment.amount_paid, Decimal("40000"))

    def test_no_penalty_before_deadline(self):
        current_time = self.payment.deadline - timedelta(minutes=1)
        self.assertEqual(
            self.payment.penalty_amount(current_time),
            Decimal("0.00")
        )

    def test_no_penalty_at_deadline(self):
        self.assertEqual(
            self.payment.penalty_amount(self.payment.deadline),
            Decimal("0.00")
        )

    def test_one_day_penalty(self):
        current_time = self.payment.deadline + timedelta(days=1)
        self.assertEqual(
            self.payment.penalty_amount(current_time),
            Decimal("1000.00")
        )

    def test_penalty_capped_at_seven_days(self):
        current_time = self.payment.deadline + timedelta(days=10)
        self.assertEqual(
            self.payment.penalty_amount(current_time),
            Decimal("7000.00")
        )

    def test_suspension_after_seven_days(self):
        current_time = self.payment.deadline + timedelta(days=8)
        self.assertTrue(
            self.payment.is_subject_to_suspension(current_time)
        )

    def test_no_suspension_within_seven_days(self):
        current_time = self.payment.deadline + timedelta(days=7)
        self.assertFalse(
            self.payment.is_subject_to_suspension(current_time)
        )

    def test_negative_payment_rejected(self):
        with self.assertRaises(ValueError):
            self.payment.record_payment("-100")

    def test_payment_exceeding_due_rejected(self):
        with self.assertRaises(ValueError):
            self.payment.record_payment("100001")


if __name__ == "__main__":
    unittest.main()