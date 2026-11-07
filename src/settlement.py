from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime


ZERO = Decimal("0")
ONE_HUNDRED = Decimal("100")


def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def can_withdraw_weight_variance(declared_weight, actual_weight):
    declared = Decimal(str(declared_weight))
    actual = Decimal(str(actual_weight))

    if declared <= ZERO or actual <= ZERO:
        raise ValueError("Weights must be positive")

    variance = abs(actual - declared) / declared
    # strictly greater than 2% allows withdrawal; exactly 2% does not
    return variance > Decimal("0.02")


def calculate_settlement(
    actual_weight_quintals,
    winning_price_per_quintal,
    moisture,
    foreign_matter,
    has_agent=False
):
    weight = Decimal(str(actual_weight_quintals))
    price = Decimal(str(winning_price_per_quintal))
    moisture = Decimal(str(moisture))
    foreign_matter = Decimal(str(foreign_matter))

    if weight <= ZERO:
        raise ValueError("Actual weight must be positive")

    if price <= ZERO:
        raise ValueError("Winning price must be positive")

    if moisture < ZERO or foreign_matter < ZERO:
        raise ValueError("Quality measurements cannot be negative")

    gross_value = weight * price

    moisture_excess = max(moisture - Decimal("12"), ZERO)
    moisture_deduction = (
        gross_value * moisture_excess / ONE_HUNDRED
    )

    foreign_matter_excess = max(
        foreign_matter - Decimal("1"), ZERO
    )
    foreign_matter_deduction = (
        gross_value * foreign_matter_excess / ONE_HUNDRED
    )

    quality_deductions = (
        moisture_deduction + foreign_matter_deduction
    )

    commission = ZERO
    if has_agent:
        commission = min(
            gross_value * Decimal("0.02"),
            Decimal("2000")
        )

    farmer_payment = gross_value - quality_deductions - commission
    market_fee = gross_value * Decimal("0.01")
    trader_total_due = gross_value + market_fee

    return {
        "gross_value": money(gross_value),
        "moisture_deduction": money(moisture_deduction),
        "foreign_matter_deduction": money(foreign_matter_deduction),
        "quality_deductions": money(quality_deductions),
        "agent_commission": money(commission),
        "farmer_payment": money(farmer_payment),
        "market_fee": money(market_fee),
        "trader_total_due": money(trader_total_due)
    }


class SettlementRecord:
    def __init__(
        self,
        lot_id,
        farmer_id,
        trader_id,
        declared_weight,
        actual_weight,
        winning_price,
        moisture,
        foreign_matter,
        agent_id=None,
        created_at=None
    ):
        self.lot_id = str(lot_id).strip()
        self.farmer_id = str(farmer_id).strip()
        self.trader_id = str(trader_id).strip()
        self.agent_id = str(agent_id).strip() if agent_id and str(agent_id).strip() else None
        self.declared_weight = Decimal(str(declared_weight))
        self.actual_weight = Decimal(str(actual_weight))
        self.winning_price = Decimal(str(winning_price))
        self.moisture = Decimal(str(moisture))
        self.foreign_matter = Decimal(str(foreign_matter))
        self.created_at = created_at or datetime.now()
        self.status = "SETTLED"

        self.calculations = calculate_settlement(
            actual_weight_quintals=self.actual_weight,
            winning_price_per_quintal=self.winning_price,
            moisture=self.moisture,
            foreign_matter=self.foreign_matter,
            has_agent=bool(self.agent_id)
        )

    @property
    def gross_value(self):
        return self.calculations["gross_value"]

    @property
    def quality_deductions(self):
        return self.calculations["quality_deductions"]

    @property
    def moisture_deduction(self):
        return self.calculations["moisture_deduction"]

    @property
    def foreign_matter_deduction(self):
        return self.calculations["foreign_matter_deduction"]

    @property
    def agent_commission(self):
        return self.calculations["agent_commission"]

    @property
    def farmer_payment(self):
        return self.calculations["farmer_payment"]

    @property
    def market_fee(self):
        return self.calculations["market_fee"]

    @property
    def trader_total_due(self):
        return self.calculations["trader_total_due"]

    def summary(self):
        agent_text = self.agent_id if self.agent_id else "None (Direct Sale)"
        return (
            f"SETTLEMENT RECORD for Lot {self.lot_id}:\n"
            f"  Farmer ID: {self.farmer_id} | Agent: {agent_text} | Winning Trader: {self.trader_id}\n"
            f"  Declared Weight: {self.declared_weight} q | Actual Weight: {self.actual_weight} q\n"
            f"  Winning Bid Price: ₹{self.winning_price} / q\n"
            f"  Gross Settlement Value: ₹{self.gross_value}\n"
            f"  Farmer Quality Deductions: ₹{self.quality_deductions} "
            f"(Moisture: ₹{self.moisture_deduction}, Foreign Matter: ₹{self.foreign_matter_deduction})\n"
            f"  Agent Commission (2%, max ₹2000): ₹{self.agent_commission}\n"
            f"  Farmer Net Payable: ₹{self.farmer_payment}\n"
            f"  Market Fee (1% on top): ₹{self.market_fee}\n"
            f"  Trader Total Payable: ₹{self.trader_total_due}"
        )


if __name__ == "__main__":
    result = calculate_settlement(
        actual_weight_quintals="100",
        winning_price_per_quintal="2400",
        moisture="13",
        foreign_matter="1.5",
        has_agent=True
    )

    for name, amount in result.items():
        print(f"{name}: ₹{amount}")
