
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta


def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


class Payment:
    def __init__(self, lot_id, trader_id, lot_value, created_at=None):
        self.lot_id = str(lot_id)
        self.trader_id = str(trader_id)
        self.lot_value = Decimal(str(lot_value))

        if self.lot_value <= 0:
            raise ValueError("Lot value must be positive")

        self.created_at = created_at or datetime.now()
        self.deadline = self.created_at + timedelta(hours=24)
        self.paid_at = None
        self.amount_paid = Decimal("0")
        self.status = "PENDING"

    def record_payment(self, amount, paid_at=None):
        amount = Decimal(str(amount))
        paid_at = paid_at or datetime.now()

        if amount <= 0:
            raise ValueError("Payment must be positive")

        if self.status == "PAID":
            raise ValueError("Payment is already complete")

        if self.amount_paid + amount > self.lot_value:
            raise ValueError("Payment exceeds the amount due")

        self.amount_paid += amount
        self.paid_at = paid_at

        if self.amount_paid == self.lot_value:
            self.status = "PAID"
        else:
            self.status = "PARTIALLY_PAID"

    def overdue_days(self, current_time=None):
        current_time = current_time or datetime.now()

        if self.status == "PAID":
            return 0

        if current_time <= self.deadline:
            return 0

        elapsed = current_time - self.deadline
        return (elapsed.days + (1 if elapsed.seconds > 0 else 0))

    def penalty_amount(self, current_time=None):
        days = self.overdue_days(current_time)
        chargeable_days = min(days, 7)

        return money(
            self.lot_value * Decimal("0.01") * chargeable_days
        )

    def is_subject_to_suspension(self, current_time=None):
        return self.overdue_days(current_time) > 7


if __name__ == "__main__":
    payment = Payment("L001", "T001", "100000")

    print("Lot:", payment.lot_id)
    print("Trader:", payment.trader_id)
    print("Amount due: ₹", payment.lot_value)
    print("Payment deadline:", payment.deadline)
    print("Status:", payment.status)
