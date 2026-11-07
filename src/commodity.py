
from decimal import Decimal


class Commodity:
    def __init__(
        self,
        commodity_id,
        name,
        msp,
        quality_parameters=None,
        bidding_increment=None
    ):
        self.commodity_id = str(commodity_id).strip()
        self.name = str(name).strip()

        if not self.commodity_id:
            raise ValueError("Commodity ID cannot be empty")

        if not self.name:
            raise ValueError("Commodity name cannot be empty")

        self.msp = Decimal(str(msp))
        if self.msp <= 0:
            raise ValueError("MSP must be positive")

        self.quality_parameters = quality_parameters or {
            "max_moisture_a": Decimal("12.0"),
            "max_foreign_matter_a": Decimal("1.0"),
            "max_damage_a": Decimal("2.0"),
            "max_moisture_b": Decimal("14.0"),
            "max_foreign_matter_b": Decimal("2.0"),
            "max_damage_b": Decimal("4.0")
        }

        if bidding_increment is not None:
            self.bidding_increment = Decimal(str(bidding_increment))
            if self.bidding_increment <= 0:
                raise ValueError("Bidding increment must be positive")
        else:
            self.bidding_increment = (
                Decimal("5") if self.msp < Decimal("3000") else Decimal("10")
            )

    def __repr__(self):
        return (
            f"Commodity(id='{self.commodity_id}', name='{self.name}', "
            f"msp={self.msp}, increment={self.bidding_increment})"
        )


if __name__ == "__main__":
    wheat = Commodity("C001", "Wheat", "2500")
    print(wheat)
