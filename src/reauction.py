from decimal import Decimal
from datetime import date, timedelta


INITIAL_FLOOR_PERCENT = Decimal("0.90")
FLOOR_REDUCTION = Decimal("0.02")
MINIMUM_FLOOR_PERCENT = Decimal("0.80")


def calculate_reauction_floor(reference_price, reauction_number):
    reference_price = Decimal(str(reference_price))

    if reference_price <= 0:
        raise ValueError("Reference price must be positive")

    if not isinstance(reauction_number, int) or isinstance(reauction_number, bool):
        raise ValueError("Re-auction number must be a non-negative integer")

    if reauction_number < 0:
        raise ValueError("Re-auction number cannot be negative")

    floor_percent = max(
        INITIAL_FLOOR_PERCENT - FLOOR_REDUCTION * reauction_number,
        MINIMUM_FLOOR_PERCENT
    )

    return reference_price * floor_percent


def next_auction_date(unsold_date):
    if not isinstance(unsold_date, date):
        raise ValueError("Unsold date must be a date")

    return unsold_date + timedelta(days=1)


if __name__ == "__main__":
    reference_price = Decimal("2500")

    for attempt in range(7):
        floor_price = calculate_reauction_floor(
            reference_price, attempt
        )
        print(
            f"Auction attempt {attempt + 1}: "
            f"floor price = ₹{floor_price}"
        )

    print("Next auction date:", next_auction_date(date.today()))