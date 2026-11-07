
import sys
import unittest
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lot import Lot


class TestLot(unittest.TestCase):

    def create_lot(self, **overrides):
        data = {
            "lot_id": "L001",
            "farmer_id": "F001",
            "commodity": "Wheat",
            "quantity_quintals": "10",
            "msp": "2500",
            "moisture": "12",
            "foreign_matter": "1",
            "damage": "2",
            "agent_id": "A001"
        }
        data.update(overrides)
        return Lot(**data)

    def test_lot_registration(self):
        lot = self.create_lot()
        self.assertEqual(lot.status, "REGISTERED")

    def test_grade_assignment(self):
        lot = self.create_lot()
        self.assertEqual(lot.grade, "A")

    def test_reference_price(self):
        lot = self.create_lot()
        self.assertEqual(lot.reference_price, Decimal("2500"))

    def test_total_reference_value(self):
        lot = self.create_lot()
        self.assertEqual(lot.total_reference_value(), Decimal("25000"))

    def test_negative_quantity_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(quantity_quintals="-1")

    def test_zero_quantity_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(quantity_quintals="0")

    def test_empty_lot_id_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(lot_id="  ")

    def test_empty_farmer_id_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(farmer_id="  ")

    def test_empty_commodity_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(commodity=" ")

    def test_negative_msp_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(msp="-1")

    def test_negative_quality_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(moisture="-1")

    def test_quality_exceeding_100_percent_rejected(self):
        with self.assertRaises(ValueError):
            self.create_lot(moisture="101")
        with self.assertRaises(ValueError):
            self.create_lot(foreign_matter="105")
        with self.assertRaises(ValueError):
            self.create_lot(damage="100.5")

    def test_auction_status_transitions(self):
        lot = self.create_lot()
        lot.mark_for_auction()
        self.assertEqual(lot.status, "IN_AUCTION")
        lot.mark_sold()
        self.assertEqual(lot.status, "SOLD")

    def test_unsold_lot(self):
        lot = self.create_lot()
        lot.mark_for_auction()
        lot.mark_unsold()
        self.assertEqual(lot.status, "UNSOLD")

    def test_cannot_sell_registered_lot(self):
        lot = self.create_lot()
        with self.assertRaises(ValueError):
            lot.mark_sold()


if __name__ == "__main__":
    unittest.main()
