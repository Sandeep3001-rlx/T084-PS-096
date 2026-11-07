
from decimal import Decimal
from datetime import datetime, timedelta


class Auction:
    def __init__(
        self,
        lot_id,
        farmer_id,
        reference_price,
        msp,
        duration_minutes=10,
        start_time=None,
        bidding_increment=None
    ):
        self.lot_id = str(lot_id).strip()
        self.farmer_id = str(farmer_id).strip()
        self.reference_price = Decimal(str(reference_price))
        self.msp = Decimal(str(msp))

        if self.reference_price <= 0 or self.msp <= 0:
            raise ValueError("Reference price and MSP must be positive")

        self.floor_price = self.reference_price * Decimal("0.90")
        self.start_time = start_time or datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.bids = []
        self.extensions = 0
        self.max_extensions = 3
        self.closed = False
        self.bidding_increment = (
            Decimal(str(bidding_increment))
            if bidding_increment is not None
            else None
        )

    def get_increment(self, current_highest):
        if self.bidding_increment is not None:
            return self.bidding_increment

        # Commodities priced below Rs 3000: Rs 5; at or above Rs 3000: Rs 10
        price_level = max(self.reference_price, current_highest)
        return Decimal("5") if price_level < Decimal("3000") else Decimal("10")

    def place_bid(self, trader_id, amount, timestamp=None):
        if self.closed:
            raise ValueError("Auction is closed")

        timestamp = timestamp or datetime.now()
        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError("Bid must be positive")

        if timestamp < self.start_time:
            raise ValueError("Auction has not started yet")

        if timestamp >= self.end_time:
            raise ValueError("Auction has ended")

        if amount < self.floor_price:
            raise ValueError("Bid is below the auction floor price")

        if self.bids:
            highest_bid = max(bid["amount"] for bid in self.bids)
            increment = self.get_increment(highest_bid)

            if amount < highest_bid + increment:
                raise ValueError("Bid does not meet the minimum increment")

        self.bids.append({
            "trader_id": str(trader_id).strip(),
            "amount": amount,
            "timestamp": timestamp
        })

        time_left = self.end_time - timestamp
        if (
            timedelta(0) <= time_left <= timedelta(seconds=60)
            and self.extensions < self.max_extensions
        ):
            self.end_time += timedelta(minutes=2)
            self.extensions += 1

        return True

    def get_highest_bid(self):
        if not self.bids:
            return None
        return sorted(
            self.bids,
            key=lambda bid: (
                -bid["amount"],
                bid["timestamp"],
                bid["trader_id"]
            )
        )[0]

    def close_auction(self):
        if self.closed:
            raise ValueError("Auction is already closed")

        self.closed = True
        return self.get_highest_bid()


if __name__ == "__main__":
    auction = Auction("L001", "F001", "2500", "2500")
    auction.place_bid("T001", "2300")
    auction.place_bid("T002", "2305")
    winner = auction.close_auction()

    print("Winning Trader:", winner["trader_id"])
    print("Winning Bid:", winner["amount"])
