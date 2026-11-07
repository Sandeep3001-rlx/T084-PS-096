import sys
import unittest
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grading import calculate_grade, calculate_reference_price


class TestGrading(unittest.TestCase):

    def test_grade_a(self):
        self.assertEqual(calculate_grade("12", "1", "2"), "A")

    def test_grade_b(self):
        self.assertEqual(calculate_grade("13", "1.5", "3"), "B")

    def test_grade_c(self):
        self.assertEqual(calculate_grade("15", "1", "2"), "C")

    def test_reference_price_a(self):
        self.assertEqual(calculate_reference_price("2500", "A"), Decimal("2500"))

    def test_reference_price_b(self):
        # 2500 - 3% = 2425
        self.assertEqual(calculate_reference_price("2500", "B"), Decimal("2425.00"))

    def test_reference_price_c(self):
        # 2500 - 8% = 2300
        self.assertEqual(calculate_reference_price("2500", "C"), Decimal("2300.00"))

    def test_moisture_boundary_12_vs_12_01(self):
        # Exactly 12.00% with other params at threshold is Grade A
        self.assertEqual(calculate_grade("12.00", "1.00", "2.00"), "A")
        # 12.01% falls to Grade B (since moisture <= 14, foreign matter <= 2, damage <= 4)
        self.assertEqual(calculate_grade("12.01", "1.00", "2.00"), "B")

    def test_foreign_matter_boundary_1_vs_1_01(self):
        self.assertEqual(calculate_grade("12.00", "1.00", "2.00"), "A")
        self.assertEqual(calculate_grade("12.00", "1.01", "2.00"), "B")

    def test_damage_boundary_2_vs_2_01(self):
        self.assertEqual(calculate_grade("12.00", "1.00", "2.00"), "A")
        self.assertEqual(calculate_grade("12.00", "1.00", "2.01"), "B")

    def test_grade_b_upper_boundary_14_vs_14_01(self):
        # Exactly 14.00% is Grade B
        self.assertEqual(calculate_grade("14.00", "2.00", "4.00"), "B")
        # 14.01% falls to Grade C
        self.assertEqual(calculate_grade("14.01", "2.00", "4.00"), "C")

    def test_grade_b_foreign_matter_boundary_2_vs_2_01(self):
        self.assertEqual(calculate_grade("14.00", "2.00", "4.00"), "B")
        self.assertEqual(calculate_grade("14.00", "2.01", "4.00"), "C")

    def test_grade_b_damage_boundary_4_vs_4_01(self):
        self.assertEqual(calculate_grade("14.00", "2.00", "4.00"), "B")
        self.assertEqual(calculate_grade("14.00", "2.00", "4.01"), "C")

    def test_invalid_grade_rejected(self):
        with self.assertRaises(ValueError):
            calculate_reference_price("2500", "D")


if __name__ == "__main__":
    unittest.main()
