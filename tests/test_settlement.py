import sys
import unittest
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from settlement import (
    calculate_settlement,
    SettlementRecord,
    can_withdraw_weight_variance
)


class TestSettlement(unittest.TestCase):

    def test_gross_value(self):
        result = calculate_settlement("100", "2400", "12", "1")
        self.assertEqual(result["gross_value"], Decimal("240000.00"))

    def test_no_quality_deductions_at_thresholds(self):
        result = calculate_settlement("10", "2500", "12", "1")
        self.assertEqual(result["quality_deductions"], Decimal("0.00"))

    def test_moisture_deduction(self):
        result = calculate_settlement("100", "2400", "13", "1")
        self.assertEqual(result["moisture_deduction"], Decimal("2400.00"))

    def test_foreign_matter_deduction(self):
        result = calculate_settlement("100", "2400", "12", "1.5")
        self.assertEqual(result["foreign_matter_deduction"], Decimal("1200.00"))

    def test_agent_commission(self):
        result = calculate_settlement(
            "10", "1000", "12", "1", has_agent=True
        )
        self.assertEqual(result["agent_commission"], Decimal("200.00"))

    def test_commission_cap(self):
        result = calculate_settlement(
            "100", "2400", "12", "1", has_agent=True
        )
        self.assertEqual(result["agent_commission"], Decimal("2000.00"))

    def test_no_agent_means_no_commission(self):
        result = calculate_settlement("10", "1000", "12", "1")
        self.assertEqual(result["agent_commission"], Decimal("0.00"))

    def test_market_fee(self):
        result = calculate_settlement("100", "2400", "12", "1")
        self.assertEqual(result["market_fee"], Decimal("2400.00"))

    def test_trader_total_due(self):
        result = calculate_settlement("100", "2400", "12", "1")
        self.assertEqual(result["trader_total_due"], Decimal("242400.00"))

    def test_farmer_net_payable_direct_sale(self):
        result = calculate_settlement("100", "2400", "12", "1", has_agent=False)
        self.assertEqual(result["farmer_payment"], Decimal("240000.00"))

    def test_farmer_net_payable_with_all_deductions(self):
        # 100 quintals @ 2400: Gross = 240,000
        # Moisture 13% (1% excess) -> 2400
        # Foreign matter 1.5% (0.5% excess) -> 1200
        # Commission (2% capped at 2000) -> 2000
        # Farmer Net Payable = 240000 - 2400 - 1200 - 2000 = 234400
        result = calculate_settlement("100", "2400", "13", "1.5", has_agent=True)
        self.assertEqual(result["gross_value"], Decimal("240000.00"))
        self.assertEqual(result["moisture_deduction"], Decimal("2400.00"))
        self.assertEqual(result["foreign_matter_deduction"], Decimal("1200.00"))
        self.assertEqual(result["quality_deductions"], Decimal("3600.00"))
        self.assertEqual(result["agent_commission"], Decimal("2000.00"))
        self.assertEqual(result["farmer_payment"], Decimal("234400.00"))
        self.assertEqual(result["market_fee"], Decimal("2400.00"))
        self.assertEqual(result["trader_total_due"], Decimal("242400.00"))

    def test_settlement_record_object(self):
        rec = SettlementRecord(
            lot_id="L001",
            farmer_id="F001",
            trader_id="T001",
            declared_weight="100",
            actual_weight="98",
            winning_price="2500",
            moisture="12",
            foreign_matter="1",
            agent_id="A001"
        )
        # Gross = 98 * 2500 = 245000
        self.assertEqual(rec.gross_value, Decimal("245000.00"))
        self.assertEqual(rec.agent_commission, Decimal("2000.00"))
        self.assertEqual(rec.market_fee, Decimal("2450.00"))
        self.assertEqual(rec.farmer_payment, Decimal("243000.00"))
        self.assertEqual(rec.trader_total_due, Decimal("247450.00"))
        self.assertIn("SETTLEMENT RECORD for Lot L001", rec.summary())

    def test_weight_variance_strictly_greater_than_two_percent(self):
        # 100 declared, 102.1 actual = 2.1% variance -> withdrawal permitted
        self.assertTrue(can_withdraw_weight_variance("100", "102.1"))
        # 100 declared, 97.9 actual = 2.1% variance -> withdrawal permitted
        self.assertTrue(can_withdraw_weight_variance("100", "97.9"))

    def test_exact_two_percent_variance_no_withdrawal(self):
        # BR-27: Exact 2% does NOT qualify for withdrawal
        self.assertFalse(can_withdraw_weight_variance("100", "102.0"))
        self.assertFalse(can_withdraw_weight_variance("100", "98.0"))

    def test_less_than_two_percent_variance_no_withdrawal(self):
        self.assertFalse(can_withdraw_weight_variance("100", "101.0"))
        self.assertFalse(can_withdraw_weight_variance("100", "99.5"))

    def test_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            calculate_settlement("-1", "2400", "12", "1")

    def test_negative_quality_rejected(self):
        with self.assertRaises(ValueError):
            calculate_settlement("10", "2400", "-1", "1")


if __name__ == "__main__":
    unittest.main()
