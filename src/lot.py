
from decimal import Decimal
from grading import calculate_grade, calculate_reference_price


class Lot:
    def __init__(
        self,
        lot_id,
        farmer_id,
        commodity,
        quantity_quintals,
        msp,
        moisture,
        foreign_matter,
        damage,
        agent_id=None
    ):
        self.lot_id = str(lot_id).strip()
        self.farmer_id = str(farmer_id).strip()
        self.commodity_id = getattr(
            commodity, "commodity_id", str(commodity).strip()
        )
        self.commodity = getattr(commodity, "name", str(commodity).strip())
        self.quantity_quintals = Decimal(str(quantity_quintals))
        self.msp = Decimal(str(msp))
        self.moisture = Decimal(str(moisture))
        self.foreign_matter = Decimal(str(foreign_matter))
        self.damage = Decimal(str(damage))
        self.agent_id = str(agent_id).strip() if agent_id is not None and str(agent_id).strip() else None

        if not self.lot_id:
            raise ValueError("Lot ID cannot be empty")

        if not self.farmer_id:
            raise ValueError("Farmer ID cannot be empty")

        if not self.commodity:
            raise ValueError("Commodity cannot be empty")

        if self.quantity_quintals <= 0:
            raise ValueError("Quantity must be positive")

        if self.msp <= 0:
            raise ValueError("MSP must be positive")

        if min(self.moisture, self.foreign_matter, self.damage) < 0:
            raise ValueError("Quality measurements cannot be negative")

        if max(self.moisture, self.foreign_matter, self.damage) > Decimal("100"):
            raise ValueError("Quality measurements cannot exceed 100%")

        self.grade = calculate_grade(
            self.moisture,
            self.foreign_matter,
            self.damage
        )

        self.reference_price = calculate_reference_price(
            self.msp,
            self.grade
        )

        self.status = "REGISTERED"

    def total_reference_value(self):
        return self.quantity_quintals * self.reference_price

    def mark_for_auction(self):
        if self.status != "REGISTERED":
            raise ValueError("Only registered lots can enter an auction")

        self.status = "IN_AUCTION"

    def mark_sold(self):
        if self.status != "IN_AUCTION":
            raise ValueError("Only lots in auction can be marked sold")

        self.status = "SOLD"

    def mark_unsold(self):
        if self.status != "IN_AUCTION":
            raise ValueError("Only lots in auction can be marked unsold")

        self.status = "UNSOLD"


if __name__ == "__main__":
    lot = Lot(
        lot_id="L001",
        farmer_id="F001",
        commodity="Wheat",
        quantity_quintals="10",
        msp="2500",
        moisture="12",
        foreign_matter="1",
        damage="2",
        agent_id="A001"
    )

    print("Lot ID:", lot.lot_id)
    print("Commodity:", lot.commodity)
    print("Quantity:", lot.quantity_quintals, "quintals")
    print("Grade:", lot.grade)
    print("Reference Price:", lot.reference_price)
    print("Total Reference Value:", lot.total_reference_value())
    print("Status:", lot.status)
