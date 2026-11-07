import sys
import unittest
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from auction import Auction


class TestAuction(unittest.TestCase):

    def test_auction_accepts_valid_bid(self):
        auction = Auction("L1", "F1", "2500", "2500")
        self.assertTrue(auction.place_bid("T1", "2300"))

    def test_bid_below_floor_is_rejected(self):
        auction = Auction("L1", "F1", "2500", "2500")
        with self.assertRaises(ValueError):
            auction.place_bid("T1", "2200")

    def test_bid_increment_is_enforced_below_3000(self):
        # Under 3000: Rs 5 increment
        auction = Auction("L1", "F1", "2500", "2500")
        auction.place_bid("T1", "2300")
        with self.assertRaises(ValueError):
            auction.place_bid("T2", "2304")
        self.assertTrue(auction.place_bid("T2", "2305"))

    def test_bid_increment_at_or_above_3000(self):
        # At or above 3000: Rs 10 increment
        auction = Auction("L2", "F2", "3500", "3500")
        # floor = 3150
        auction.place_bid("T1", "3200")
        with self.assertRaises(ValueError):
            auction.place_bid("T2", "3205")
        with self.assertRaises(ValueError):
            auction.place_bid("T2", "3209")
        self.assertTrue(auction.place_bid("T2", "3210"))

    def test_bid_increment_at_exact_3000(self):
        auction = Auction("L3", "F3", "3000", "3000")
        # floor = 2700
        auction.place_bid("T1", "2800")
        # Since reference price is 3000 (at or above 3000), required increment is 10
        with self.assertRaises(ValueError):
            auction.place_bid("T2", "2805")
        self.assertTrue(auction.place_bid("T2", "2810"))

    def test_highest_bid_wins(self):
        auction = Auction("L1", "F1", "2500", "2500")
        auction.place_bid("T1", "2300")
        auction.place_bid("T2", "2310")
        winner = auction.close_auction()
        self.assertEqual(winner["trader_id"], "T2")

    def test_auction_without_bids(self):
        auction = Auction("L1", "F1", "2500", "2500")
        self.assertIsNone(auction.close_auction())

    def test_closed_auction_rejects_bid(self):
        auction = Auction("L1", "F1", "2500", "2500")
        auction.close_auction()
        with self.assertRaises(ValueError):
            auction.place_bid("T1", "2300")

    def test_auction_extension_triggered_in_last_60_seconds(self):
        start = datetime(2026, 10, 19, 10, 0, 0)
        auction = Auction("L1", "F1", "2500", "2500", start_time=start)
        # End time initially 10:10:00
        initial_end = auction.end_time

        # Bid arrives at 10:09:15 (45s before close)
        bid_time = start + timedelta(minutes=9, seconds=15)
        auction.place_bid("T1", "2300", timestamp=bid_time)

        self.assertEqual(auction.extensions, 1)
        self.assertEqual(auction.end_time, initial_end + timedelta(minutes=2))

    def test_auction_extension_at_exactly_60_seconds(self):
        start = datetime(2026, 10, 19, 10, 0, 0)
        auction = Auction("L1", "F1", "2500", "2500", start_time=start)
        initial_end = auction.end_time

        # Exactly 60s before close: 10:09:00
        bid_time = start + timedelta(minutes=9)
        auction.place_bid("T1", "2300", timestamp=bid_time)

        self.assertEqual(auction.extensions, 1)
        self.assertEqual(auction.end_time, initial_end + timedelta(minutes=2))

    def test_max_three_extensions_limit(self):
        start = datetime(2026, 10, 19, 10, 0, 0)
        auction = Auction("L1", "F1", "2500", "2500", start_time=start)

        # Trigger extension 1 at 10:09:30 -> extends to 10:12:00
        auction.place_bid("T1", "2300", timestamp=start + timedelta(minutes=9, seconds=30))
        self.assertEqual(auction.extensions, 1)

        # Trigger extension 2 at 10:11:30 -> extends to 10:14:00
        auction.place_bid("T2", "2310", timestamp=start + timedelta(minutes=11, seconds=30))
        self.assertEqual(auction.extensions, 2)

        # Trigger extension 3 at 10:13:30 -> extends to 10:16:00
        auction.place_bid("T1", "2320", timestamp=start + timedelta(minutes=13, seconds=30))
        self.assertEqual(auction.extensions, 3)

        # Bid in final second of 3rd extension at 10:15:59
        end_after_ext3 = auction.end_time
        auction.place_bid("T2", "2330", timestamp=start + timedelta(minutes=15, seconds=59))
        # Extensions capped at 3, end_time does not increase
        self.assertEqual(auction.extensions, 3)
        self.assertEqual(auction.end_time, end_after_ext3)

    def test_bid_after_end_time_rejected(self):
        start = datetime(2026, 10, 19, 10, 0, 0)
        auction = Auction("L1", "F1", "2500", "2500", start_time=start)
        bid_time = start + timedelta(minutes=10, seconds=1)
        with self.assertRaises(ValueError):
            auction.place_bid("T1", "2300", timestamp=bid_time)

    def test_tie_breaking_different_timestamps(self):
        # BR-15: Earliest timestamp wins when amounts are identical
        auction = Auction("L1", "F1", "2500", "2500")
        t1 = datetime(2026, 10, 19, 10, 2, 0)
        t2 = datetime(2026, 10, 19, 10, 3, 0)
        # Directly insert identical amounts with different timestamps
        auction.bids.append({"trader_id": "T002", "amount": Decimal("2400"), "timestamp": t2})
        auction.bids.append({"trader_id": "T001", "amount": Decimal("2400"), "timestamp": t1})
        winner = auction.close_auction()
        self.assertEqual(winner["trader_id"], "T001")

    def test_tie_breaking_identical_timestamps_lower_trader_id_wins(self):
        # BR-15: Lower trader ID wins when amounts and timestamps are identical
        auction = Auction("L1", "F1", "2500", "2500")
        t = datetime(2026, 10, 19, 10, 2, 0, 123456)
        auction.bids.append({"trader_id": "T002", "amount": Decimal("2400"), "timestamp": t})
        auction.bids.append({"trader_id": "T001", "amount": Decimal("2400"), "timestamp": t})
        winner = auction.close_auction()
        self.assertEqual(winner["trader_id"], "T001")


if __name__ == "__main__":
    unittest.main()
