import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from main import process_commands


class TestCommandWorkflow(unittest.TestCase):
    def run_commands(self, commands):
        with tempfile.TemporaryDirectory() as directory:
            command_file = Path(directory) / "commands.csv"
            command_file.write_text(commands, encoding="utf-8")

            with patch("builtins.print"):
                return process_commands(command_file)

    def test_register_trader_and_lot(self):
        traders, lots, auctions = self.run_commands(
            "REGISTER_TRADER,T001,Trader One,10000\n"
            "REGISTER_LOT,L001,F001,Wheat,10,2500,12,1,2\n"
        )

        self.assertIn("T001", traders)
        self.assertIn("L001", lots)
        self.assertEqual(len(auctions), 0)

    def test_duplicate_trader_is_rejected(self):
        traders, _, _ = self.run_commands(
            "REGISTER_TRADER,T001,Trader One,10000\n"
            "REGISTER_TRADER,T001,Trader Two,15000\n"
        )

        self.assertEqual(len(traders), 1)

    def test_auction_winner_and_market_fee(self):
        traders, lots, auctions = self.run_commands(
            "REGISTER_TRADER,T001,Trader One,100000\n"
            "REGISTER_TRADER,T002,Trader Two,150000\n"
            "REGISTER_LOT,L001,F001,Wheat,10,2500,12,1,2\n"
            "RUN_AUCTION,L001\n"
            "PLACE_BID,L001,T001,2300\n"
            "PLACE_BID,L001,T002,2305\n"
            "PLACE_BID,L001,T001,2310\n"
            "CLOSE_AUCTION,L001\n"
        )

        self.assertEqual(lots["L001"].status, "SOLD")
        self.assertEqual(traders["T001"].outstanding_dues, 23331)
        self.assertEqual(traders["T002"].outstanding_dues, 0)
        self.assertTrue(auctions["L001"].closed)

    def test_unknown_command_does_not_stop_processing(self):
        traders, _, _ = self.run_commands(
            "UNKNOWN_COMMAND\n"
            "REGISTER_TRADER,T001,Trader One,10000\n"
        )

        self.assertIn("T001", traders)

    def test_farmer_agent_commodity_registration(self):
        res = self.run_commands(
            "REGISTER_FARMER,F001,Ramesh Kumar\n"
            "REGISTER_FARMER,F001,Duplicate Farmer\n"
            "REGISTER_AGENT,A001,Suresh Agency\n"
            "REGISTER_AGENT,A001,Duplicate Agent\n"
            "REGISTER_COMMODITY,C001,Wheat,2500,5\n"
            "REGISTER_COMMODITY,C001,Wheat,2500,5\n"
        )

        self.assertEqual(len(res.farmers), 1)
        self.assertIn("F001", res.farmers)
        self.assertEqual(res.farmers["F001"].name, "Ramesh Kumar")

        self.assertEqual(len(res.agents), 1)
        self.assertIn("A001", res.agents)

        self.assertIn("C001", res.commodities)
        self.assertEqual(res.commodities["C001"].bidding_increment, Decimal("5"))

    def test_weigh_in_and_settlement_workflow(self):
        res = self.run_commands(
            "REGISTER_TRADER,T001,Trader One,100000\n"
            "REGISTER_LOT,L001,F001,Wheat,100,2500,12,1,2,A001\n"
            "RUN_AUCTION,L001\n"
            "PLACE_BID,L001,T001,2300\n"
            "CLOSE_AUCTION,L001\n"
            "WEIGH_IN,L001,98\n"
        )

        self.assertIn("L001", res.settlements)
        settlement = res.settlements["L001"]
        self.assertEqual(settlement.actual_weight, Decimal("98"))
        # 98 quintals @ 2300: Gross = 225,400.00
        self.assertEqual(settlement.gross_value, Decimal("225400.00"))
        # Market fee = 2254.00, Trader total due = 227654.00
        self.assertEqual(settlement.trader_total_due, Decimal("227654.00"))
        self.assertEqual(res.traders["T001"].outstanding_dues, Decimal("227654.00"))

    def test_record_payment_workflow(self):
        res = self.run_commands(
            "REGISTER_TRADER,T001,Trader One,100000\n"
            "REGISTER_LOT,L001,F001,Wheat,10,2500,12,1,2\n"
            "RUN_AUCTION,L001\n"
            "PLACE_BID,L001,T001,2300\n"
            "CLOSE_AUCTION,L001\n"
            "RECORD_PAYMENT,L001,T001,10000\n"
        )

        # Initial due: 10 * 2300 * 1.01 = 23230.00
        # Paid: 10000.00 -> Remaining: 13230.00
        self.assertEqual(res.traders["T001"].outstanding_dues, Decimal("13230.00"))

    def test_unsold_auction_workflow(self):
        traders, lots, auctions = self.run_commands(
            "REGISTER_LOT,L001,F001,Wheat,10,2500,12,1,2\n"
            "RUN_AUCTION,L001\n"
            "CLOSE_AUCTION,L001\n"
        )

        self.assertEqual(lots["L001"].status, "UNSOLD")
        self.assertTrue(auctions["L001"].closed)

    def test_run_complete_workflow_file(self):
        file_path = Path(__file__).resolve().parents[1] / "sample_data" / "complete_workflow.csv"
        with patch("builtins.print"):
            res = process_commands(file_path)

        self.assertEqual(len(res.farmers), 3)
        self.assertEqual(len(res.agents), 2)
        self.assertEqual(len(res.traders), 3)
        self.assertEqual(len(res.lots), 3)
        self.assertEqual(len(res.auctions), 3)
        self.assertEqual(res.lots["L001"].status, "SOLD")
        self.assertEqual(res.lots["L002"].status, "SOLD")
        self.assertEqual(res.lots["L003"].status, "UNSOLD")


if __name__ == "__main__":
    unittest.main()
