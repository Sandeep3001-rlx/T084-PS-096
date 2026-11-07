
from decimal import Decimal


def calculate_grade(moisture, foreign_matter, damage):
    moisture = Decimal(str(moisture))
    foreign_matter = Decimal(str(foreign_matter))
    damage = Decimal(str(damage))

    if moisture <= Decimal("12") and foreign_matter <= Decimal("1") and damage <= Decimal("2"):
        return "A"

    if moisture <= Decimal("14") and foreign_matter <= Decimal("2") and damage <= Decimal("4"):
        return "B"

    return "C"


def calculate_reference_price(msp, grade):
    msp = Decimal(str(msp))

    if grade == "A":
        return msp
    elif grade == "B":
        return msp * Decimal("0.97")
    elif grade == "C":
        return msp * Decimal("0.92")
    else:
        raise ValueError("Invalid grade")


if __name__ == "__main__":
    grade = calculate_grade("12.00", "1.00", "2.00")
    price = calculate_reference_price("2500", grade)

    print("Grade:", grade)
    print("Reference price:", price)
