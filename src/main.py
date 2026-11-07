import csv
import sys
from pathlib import Path
from decimal import Decimal

# Ensure stdout handles UTF-8 (Rupee symbol etc.) on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from trader import Trader
from lot import Lot
from auction import Auction
from farmer import Farmer
from agent import CommissionAgent
from commodity import Commodity
from settlement import SettlementRecord, calculate_settlement, can_withdraw_weight_variance


class CommandExecutionResult(tuple):
    def __new__(
        cls,
        traders,
        lots,
        auctions,
        settlements=None,
        farmers=None,
        agents=None,
        commodities=None
    ):
        instance = super().__new__(cls, (traders, lots, auctions))
        instance.traders = traders
        instance.lots = lots
        instance.auctions = auctions
        instance.settlements = settlements or {}
        instance.farmers = farmers or {}
        instance.agents = agents or {}
        instance.commodities = commodities or {}
        return instance


def process_commands(command_file):
    traders = {}
    lots = {}
    auctions = {}
    settlements = {}
    farmers = {}
    agents = {}
    commodities = {}

    def require_count(row, count):
        if len(row) != count:
            raise ValueError(
                f"Incorrect number of command fields: expected {count}, got {len(row)}"
            )

    with open(command_file, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, start=1):
            if not row or not any(value.strip() for value in row):
                continue

            command = row[0].strip().upper()

            try:
                if command == "REGISTER_FARMER":
                    require_count(row, 3)
                    farmer_id = row[1].strip()
                    name = row[2].strip()

                    if not farmer_id or not name:
                        raise ValueError("Farmer ID and name are required")

                    if farmer_id in farmers:
                        raise ValueError(f"Farmer ID {farmer_id} already exists")

                    farmers[farmer_id] = Farmer(farmer_id, name)
                    print(f"SUCCESS: Farmer {farmer_id} registered. Name: {name}")

                elif command == "REGISTER_AGENT":
                    require_count(row, 3)
                    agent_id = row[1].strip()
                    name = row[2].strip()

                    if not agent_id or not name:
                        raise ValueError("Agent ID and name are required")

                    if agent_id in agents:
                        raise ValueError(f"Agent ID {agent_id} already exists")

                    agents[agent_id] = CommissionAgent(agent_id, name)
                    print(
                        f"SUCCESS: Commission agent {agent_id} registered. "
                        f"Name: {name}"
                    )

                elif command == "REGISTER_COMMODITY":
                    if len(row) not in (4, 5):
                        raise ValueError(
                            "Expected 4 or 5 fields for REGISTER_COMMODITY"
                        )
                    commodity_id = row[1].strip()
                    name = row[2].strip()
                    msp = row[3].strip()
                    increment = row[4].strip() if len(row) == 5 else None

                    if not commodity_id or not name:
                        raise ValueError(
                            "Commodity ID and name are required"
                        )

                    if commodity_id in commodities:
                        raise ValueError(
                            f"Commodity ID {commodity_id} already exists"
                        )

                    comm = Commodity(
                        commodity_id=commodity_id,
                        name=name,
                        msp=msp,
                        bidding_increment=increment
                    )
                    commodities[commodity_id] = comm
                    commodities[name.lower()] = comm

                    print(
                        f"SUCCESS: Commodity {commodity_id} ({name}) registered. "
                        f"MSP: ₹{comm.msp}. Bidding increment: ₹{comm.bidding_increment}"
                    )

                elif command == "REGISTER_TRADER":
                    require_count(row, 4)
                    trader_id = row[1].strip()

                    if not trader_id or not row[2].strip():
                        raise ValueError("Trader ID and name are required")

                    if trader_id in traders:
                        raise ValueError("Trader ID already exists")

                    traders[trader_id] = Trader(
                        trader_id, row[2].strip(), row[3].strip()
                    )

                    print(
                        f"SUCCESS: Trader {trader_id} registered. "
                        f"Credit limit: ₹{traders[trader_id].credit_limit}"
                    )

                elif command == "REGISTER_LOT":
                    if len(row) not in (9, 10):
                        raise ValueError(
                            "Expected 9 or 10 fields for REGISTER_LOT"
                        )

                    lot_id = row[1].strip()

                    if lot_id in lots:
                        raise ValueError("Lot ID already exists")

                    farmer_id = row[2].strip()
                    commodity_input = row[3].strip()
                    agent_id = (
                        row[9].strip()
                        if len(row) == 10 and row[9].strip()
                        else None
                    )

                    lot = Lot(
                        lot_id=lot_id,
                        farmer_id=farmer_id,
                        commodity=commodity_input,
                        quantity_quintals=row[4].strip(),
                        msp=row[5].strip(),
                        moisture=row[6].strip(),
                        foreign_matter=row[7].strip(),
                        damage=row[8].strip(),
                        agent_id=agent_id
                    )

                    lots[lot_id] = lot

                    print(
                        f"SUCCESS: Lot {lot_id} registered. "
                        f"Grade: {lot.grade}. "
                        f"Reference price: ₹{lot.reference_price}"
                    )

                elif command == "RUN_AUCTION":
                    require_count(row, 2)
                    lot_id = row[1].strip()

                    if lot_id not in lots:
                        raise ValueError("Lot does not exist")

                    lot = lots[lot_id]

                    if lot_id in auctions:
                        raise ValueError("Auction already exists for this lot")

                    if lot.status != "REGISTERED":
                        raise ValueError("Lot is not available for auction")

                    # Look up if commodity has custom bidding increment
                    bidding_increment = None
                    if lot.commodity.lower() in commodities:
                        bidding_increment = commodities[lot.commodity.lower()].bidding_increment
                    elif lot.commodity_id in commodities:
                        bidding_increment = commodities[lot.commodity_id].bidding_increment

                    auction = Auction(
                        lot.lot_id,
                        lot.farmer_id,
                        lot.reference_price,
                        lot.msp,
                        bidding_increment=bidding_increment
                    )

                    lot.mark_for_auction()
                    auctions[lot_id] = auction

                    print(
                        f"SUCCESS: Auction opened for {lot_id}. "
                        f"Floor price per quintal: ₹{auction.floor_price}"
                    )

                elif command == "PLACE_BID":
                    if len(row) not in (4, 5):
                        raise ValueError("Expected 4 or 5 fields for PLACE_BID")

                    lot_id = row[1].strip()
                    trader_id = row[2].strip()
                    amount = Decimal(row[3].strip())

                    if lot_id not in auctions:
                        raise ValueError("Auction does not exist")

                    if trader_id not in traders:
                        raise ValueError("Trader does not exist")

                    lot = lots[lot_id]
                    auction = auctions[lot_id]
                    trader = traders[trader_id]

                    proposed_exposure = amount * lot.quantity_quintals

                    # Temporarily pop previous winning exposure for this lot if trader was winning
                    previous_exposure = trader.winning_bids.pop(lot_id, None)

                    eligible, reason = trader.check_eligibility(proposed_exposure)

                    if previous_exposure is not None:
                        trader.winning_bids[lot_id] = previous_exposure

                    if not eligible:
                        raise ValueError(
                            f"Trader {trader_id} ineligible: {reason}"
                        )

                    previous_winner = None
                    if auction.bids:
                        previous_winner = max(
                            auction.bids,
                            key=lambda bid: bid["amount"]
                        )["trader_id"]

                    auction.place_bid(trader_id, amount)

                    if previous_winner is not None and previous_winner != trader_id:
                        traders[previous_winner].lose_lot(lot_id)

                    trader.place_bid(lot_id, proposed_exposure)

                    print(
                        f"SUCCESS: Bid accepted. Lot {lot_id}, "
                        f"Trader {trader_id}, ₹{amount} per quintal"
                    )

                elif command == "CLOSE_AUCTION":
                    require_count(row, 2)
                    lot_id = row[1].strip()

                    if lot_id not in auctions:
                        raise ValueError("Auction does not exist")

                    auction = auctions[lot_id]
                    lot = lots[lot_id]

                    winner = auction.close_auction()

                    if winner is None:
                        lot.mark_unsold()
                        print(f"UNSOLD: Lot {lot_id} received no bids")
                    else:
                        lot.mark_sold()
                        winning_trader = traders[winner["trader_id"]]

                        # Generate settlement record with declared weight (pending weigh-in)
                        settlement_record = SettlementRecord(
                            lot_id=lot.lot_id,
                            farmer_id=lot.farmer_id,
                            trader_id=winner["trader_id"],
                            declared_weight=lot.quantity_quintals,
                            actual_weight=lot.quantity_quintals,
                            winning_price=winner["amount"],
                            moisture=lot.moisture,
                            foreign_matter=lot.foreign_matter,
                            agent_id=lot.agent_id
                        )

                        settlements[lot_id] = settlement_record
                        winning_trader.record_due(
                            lot_id, settlement_record.trader_total_due
                        )

                        print(
                            f"SOLD: Lot {lot_id}. "
                            f"Winning trader: {winner['trader_id']}. "
                            f"Bid: ₹{winner['amount']} per quintal. "
                            f"Gross value: ₹{settlement_record.gross_value}. "
                            f"Trader total due including 1% market fee: "
                            f"₹{settlement_record.trader_total_due}"
                        )
                        print(
                            f"SETTLEMENT SUMMARY: Lot {lot_id} | "
                            f"Farmer Net Payable: ₹{settlement_record.farmer_payment} | "
                            f"Agent Commission: ₹{settlement_record.agent_commission} | "
                            f"Quality Deductions: ₹{settlement_record.quality_deductions} | "
                            f"Market Fee: ₹{settlement_record.market_fee}"
                        )

                elif command in ("WEIGH_IN", "SETTLE_LOT"):
                    if len(row) not in (2, 3):
                        raise ValueError(
                            f"Expected 2 or 3 fields for {command}"
                        )

                    lot_id = row[1].strip()
                    if lot_id not in lots:
                        raise ValueError("Lot does not exist")

                    lot = lots[lot_id]
                    if lot_id not in auctions:
                        raise ValueError("Auction does not exist for this lot")

                    auction = auctions[lot_id]
                    winner = auction.get_highest_bid()
                    if winner is None:
                        raise ValueError("Lot was not sold in auction")

                    actual_weight = (
                        Decimal(row[2].strip())
                        if len(row) == 3
                        else lot.quantity_quintals
                    )

                    # Check weight variance vs declared weight
                    if can_withdraw_weight_variance(lot.quantity_quintals, actual_weight):
                        diff_pct = (
                            abs(actual_weight - lot.quantity_quintals)
                            / lot.quantity_quintals * Decimal("100")
                        )
                        print(
                            f"NOTICE: Actual weight differs from declared weight by "
                            f"{diff_pct:.2f}% (> 2%). Trader may withdraw within 30 min."
                        )

                    settlement_record = SettlementRecord(
                        lot_id=lot.lot_id,
                        farmer_id=lot.farmer_id,
                        trader_id=winner["trader_id"],
                        declared_weight=lot.quantity_quintals,
                        actual_weight=actual_weight,
                        winning_price=winner["amount"],
                        moisture=lot.moisture,
                        foreign_matter=lot.foreign_matter,
                        agent_id=lot.agent_id
                    )

                    # Adjust trader dues if previously recorded
                    winning_trader = traders[winner["trader_id"]]
                    if lot_id in settlements:
                        old_due = settlements[lot_id].trader_total_due
                        winning_trader.outstanding_dues -= old_due

                    settlements[lot_id] = settlement_record
                    winning_trader.outstanding_dues += settlement_record.trader_total_due

                    print(f"SUCCESS: Settlement finalized for Lot {lot_id}.")
                    print(settlement_record.summary())

                elif command in ("RECORD_PAYMENT", "MAKE_PAYMENT"):
                    require_count(row, 4)
                    lot_id = row[1].strip()
                    trader_id = row[2].strip()
                    amount = Decimal(row[3].strip())

                    if trader_id not in traders:
                        raise ValueError("Trader does not exist")

                    trader = traders[trader_id]
                    trader.make_payment(amount)

                    print(
                        f"SUCCESS: Payment of ₹{amount} received from Trader {trader_id} "
                        f"for Lot {lot_id}. Remaining dues: ₹{trader.outstanding_dues}"
                    )

                else:
                    raise ValueError(f"Unknown command: {command}")

            except (ValueError, ArithmeticError) as error:
                print(f"ERROR on line {line_number}: {error}")

    print("\nRegistered traders:", len(traders))
    print("Registered lots:", len(lots))
    print("Auctions opened:", len(auctions))

    return CommandExecutionResult(
        traders=traders,
        lots=lots,
        auctions=auctions,
        settlements=settlements,
        farmers=farmers,
        agents=agents,
        commodities=commodities
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/main.py sample_data/commands.csv")
        sys.exit(1)

    command_file = Path(sys.argv[1])

    if not command_file.is_file():
        print(f"Command file not found: {command_file}")
        sys.exit(1)

    process_commands(command_file)
