import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent import CommissionAgent


class TestCommissionAgent(unittest.TestCase):

    def test_valid_agent_registration(self):
        agent = CommissionAgent("A001", "Suresh Agency")
        self.assertEqual(agent.agent_id, "A001")
        self.assertEqual(agent.name, "Suresh Agency")

    def test_empty_agent_id_rejected(self):
        with self.assertRaises(ValueError):
            CommissionAgent("", "Suresh Agency")
        with self.assertRaises(ValueError):
            CommissionAgent("   ", "Suresh Agency")

    def test_empty_agent_name_rejected(self):
        with self.assertRaises(ValueError):
            CommissionAgent("A001", "")
        with self.assertRaises(ValueError):
            CommissionAgent("A001", "   ")


if __name__ == "__main__":
    unittest.main()
