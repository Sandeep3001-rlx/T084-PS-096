
from decimal import Decimal


class Trader:
    def __init__(self, trader_id, name, security_deposit):
        self.trader_id = str(trader_id).strip()
        self.name = str(name).strip()

        if not self.trader_id:
            raise ValueError("Trader ID cannot be empty")

        if not self.name:
            raise ValueError("Trader name cannot be empty")

        self.security_deposit = Decimal(str(security_deposit))

        if self.security_deposit < 0:
            raise ValueError("Security deposit cannot be negative")

        self.credit_limit = self.security_deposit * Decimal("10")
        self.outstanding_dues = Decimal("0")
        self.winning_bids = {}
        self.overdue_days = 0
        self.suspended = False

    def current_exposure(self):
        return self.outstanding_dues + sum(
            self.winning_bids.values(), Decimal("0")
        )

    def check_eligibility(self, bid_amount):
        bid_amount = Decimal(str(bid_amount))

        if self.suspended:
            return False, f"Trader {self.trader_id} is suspended"

        if self.overdue_days > 7:
            return (
                False,
                f"Trader {self.trader_id} has overdue dues of "
                f"{self.overdue_days} days (> 7 days allowed)"
            )

        if bid_amount <= 0:
            return False, "Bid amount must be positive"

        total_exposure = self.current_exposure() + bid_amount
        if total_exposure > self.credit_limit:
            return (
                False,
                f"Total exposure ₹{total_exposure} exceeds credit limit "
                f"₹{self.credit_limit} for trader {self.trader_id}"
            )

        return True, ""

    def can_bid(self, bid_amount):
        eligible, _ = self.check_eligibility(bid_amount)
        return eligible

    def place_bid(self, lot_id, bid_amount):
        bid_amount = Decimal(str(bid_amount))

        eligible, reason = self.check_eligibility(bid_amount)
        if not eligible:
            raise ValueError(f"Bid rejected: {reason}")

        self.winning_bids[str(lot_id)] = bid_amount

    def lose_lot(self, lot_id):
        self.winning_bids.pop(str(lot_id), None)

    def record_due(self, lot_id, amount):
        lot_id = str(lot_id)
        amount = Decimal(str(amount))

        if amount < 0:
            raise ValueError("Due amount cannot be negative")

        self.winning_bids.pop(lot_id, None)
        self.outstanding_dues += amount

    def make_payment(self, amount):
        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError("Payment must be positive")

        if amount > self.outstanding_dues:
            raise ValueError("Payment exceeds outstanding dues")

        self.outstanding_dues -= amount


if __name__ == "__main__":
    trader = Trader("T001", "Demo Trader", "10000")

    print("Trader:", trader.name)
    print("Credit Limit:", trader.credit_limit)
    print("Can bid ₹50000:", trader.can_bid("50000"))
    print("Can bid ₹100001:", trader.can_bid("100001"))
