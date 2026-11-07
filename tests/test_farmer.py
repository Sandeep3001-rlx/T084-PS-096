import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from farmer import Farmer


class TestFarmer(unittest.TestCase):

    def test_valid_farmer_registration(self):
        farmer = Farmer("F001", "Ramesh Kumar")
        self.assertEqual(farmer.farmer_id, "F001")
        self.assertEqual(farmer.name, "Ramesh Kumar")

    def test_empty_farmer_id_rejected(self):
        with self.assertRaises(ValueError):
            Farmer("", "Ramesh Kumar")
        with self.assertRaises(ValueError):
            Farmer("   ", "Ramesh Kumar")

    def test_empty_farmer_name_rejected(self):
        with self.assertRaises(ValueError):
            Farmer("F001", "")
        with self.assertRaises(ValueError):
            Farmer("F001", "   ")


if __name__ == "__main__":
    unittest.main()
