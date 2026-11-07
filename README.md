# Agri Mandi Electronic Auction and Commission Settlement Engine

## 1. Project Title
**Agri Mandi Electronic Auction and Commission Settlement Engine**

---

## 2. Problem Statement
**Problem Statement ID:** PS-096  
Regulated agricultural markets (Mandis) require an automated, transparent, and rule-compliant backend engine to register farmer produce lots with assayed quality parameters, conduct timed electronic auctions with price bands and minimum support price (MSP) floors, enforce trader eligibility and exposure limits, settle payments to farmers after applying quality deductions, market fees, and commission caps, and track trader dues and payments.

---

## 3. Team Details
- **Team ID:** T084
- **Section:** CSD
- **Team Members:**
  1. **Sai Srujan Reddy M R** – 1AT24CG068
  2. **Sandeep R** – 1AT24CG069
- **GitHub Repository:** [https://github.com/Sandeep3001-rlx/T084-PS-096](https://github.com/Sandeep3001-rlx/T084-PS-096)

---

## 4. Project Overview
This project provides a command-file-driven backend system in Python that automates the core electronic auction and financial settlement operations of a regulated agricultural market.

The engine processes batch command files (CSV) and enforces all official business rules:
- **Entity Registration:** Farmers, Commission Agents, Commodities, and Traders.
- **Trader Exposure & Credit Limit:** Credit limit is set to 10× the security deposit. Bids are validated against current exposure (outstanding dues + active winning bids + proposed bid). Traders with dues older than 7 days or suspended status are strictly barred from bidding.
- **Automated Quality Grading:** Analyzes assayed moisture, foreign matter, and damage percentages to assign Grade A, B, or C.
- **Reference Price & Floor:** Reference price is computed from MSP (Grade A = 100%, Grade B = 97%, Grade C = 92%). Initial auction floor is set at 90% of reference price.
- **Timed Auctions & Extensions:** Enforces price floors and increment rules (₹5 per quintal for prices < ₹3,000; ₹10 per quintal for prices ≥ ₹3,000). Extends auction by 2 minutes when bids arrive during the final 60 seconds (up to 3 extensions).
- **Weigh-Bridge Settlement:** Supports weigh-bridge actual weight adjustments, detects weight variance > 2% allowing withdrawal, applies moisture and foreign matter quality deductions, caps commission at ₹2,000 (₹0 for direct farmer sale), charges 1% market fee on gross value, and computes farmer net payable and trader total payable using high-precision `Decimal` arithmetic.
- **Trader Dues & Payments:** Records trader payables and tracks payment receipts against dues.

No graphical user interface or frontend is required.

---

## 5. Technologies Used
- **Python 3.10+** (Tested on Python 3.12.7)
- **Standard Library Only:**
  - `decimal` (Fixed-point and floating-point arithmetic for rupee calculations)
  - `datetime` & `timedelta` (Auction timing, extension window detection, payment deadlines)
  - `csv` (Command file ingestion)
  - `pathlib` (Cross-platform file path resolution)
  - `unittest` (Comprehensive automated unit testing)
- **Zero External Third-Party Dependencies** (No external packages required)

---

## 6. Project Folder Structure
```text
T084-PS-096/
├── .gitignore                      # Git ignore file for Python caches and OS files
├── README.md                       # Complete project documentation
├── design/
│   ├── business_rules.md.txt       # Register of business rules (BR-01 to BR-46)
│   ├── decision_log.md.txt         # Architecture and rule decision log
│   └── design_document.md.txt      # High-level architecture and data model specification
├── sample_data/
│   ├── commands.csv                # Standard sample command input file
│   └── complete_workflow.csv       # Comprehensive end-to-end sample workflow file
├── src/
│   ├── __init__.py                 # Package marker
│   ├── agent.py                    # Commission Agent registration model
│   ├── auction.py                  # Timed electronic auction management and bidding
│   ├── commodity.py                # Commodity registration and increment rules
│   ├── farmer.py                   # Farmer registration model
│   ├── grading.py                  # Automated quality grading and reference price logic
│   ├── lot.py                      # Agricultural lot registration and status state machine
│   ├── main.py                     # Command file processor and application entry point
│   ├── payment.py                  # Payment deadline, overdue tracking, and penalty calculations
│   ├── reauction.py                # Re-auction floor reduction (2% per attempt, min 80%)
│   ├── settlement.py               # Weigh-in settlement, quality deductions, and commission
│   └── trader.py                   # Trader registration, credit exposure, and ledger
└── tests/
    ├── __init__.py                 # Test package marker
    ├── test_agent.py               # Unit tests for Commission Agent
    ├── test_auction.py             # Unit tests for auction bidding, floors, increments, extensions
    ├── test_commodity.py           # Unit tests for Commodity registration and rules
    ├── test_farmer.py              # Unit tests for Farmer registration
    ├── test_grading.py             # Unit tests for grading rules and reference prices
    ├── test_lot.py                 # Unit tests for lot registration and validations
    ├── test_main.py                # Unit tests for command processor and full workflow
    ├── test_payment.py             # Unit tests for payment deadlines and penalties
    ├── test_reauction.py           # Unit tests for re-auction floor reduction
    ├── test_settlement.py          # Unit tests for quality deductions, fees, commission, and net payable
    └── test_trader.py              # Unit tests for trader credit limit, exposure, and dues
```

---

## 7. Installation Instructions

1. **Verify Python Installation (Python 3.10 or higher required):**
   ```powershell
   python --version
   ```

2. **Clone the Repository (or navigate to project directory):**
   ```powershell
   cd C:\Users\Sandeep\Desktop\T084-PS-096
   ```

3. **No External Packages Required:**
   The project is built entirely on the Python standard library. No `pip install` commands are needed.

---

## 8. Dependencies
- Python standard library (`decimal`, `datetime`, `csv`, `pathlib`, `unittest`, `sys`).
- Optional: `pytest` can be used to run the tests if installed in the environment (`python -m unittest` is fully supported natively).

---

## 9. How to Execute the Project

### Running the Standard Sample Command File
```powershell
python src/main.py sample_data/commands.csv
```

### Running the Complete End-to-End Workflow Command File
```powershell
python src/main.py sample_data/complete_workflow.csv
```

### Executing Any Custom Command File
```powershell
python src/main.py <path-to-command-file.csv>
```

---

## 10. How to Execute Tests

Run the complete test suite using Python's built-in `unittest` runner:

```powershell
python -m unittest discover tests
```

To run individual test modules:
```powershell
python -m unittest tests/test_grading.py
python -m unittest tests/test_auction.py
python -m unittest tests/test_settlement.py
python -m unittest tests/test_trader.py
python -m unittest tests/test_main.py
```

---

## 11. Sample Input and Output

### Sample Input (`sample_data/complete_workflow.csv`)
```csv
REGISTER_FARMER,F001,Ramesh Patel
REGISTER_AGENT,A001,Kisan Seva Kendra
REGISTER_COMMODITY,C001,Wheat,2500,5
REGISTER_TRADER,T001,Apex Agro Traders,100000
REGISTER_LOT,L001,F001,Wheat,100,2500,11.5,0.8,1.5,A001
RUN_AUCTION,L001
PLACE_BID,L001,T001,2300
CLOSE_AUCTION,L001
WEIGH_IN,L001,99.5
RECORD_PAYMENT,L001,T001,100000
```

### Sample Output
```text
SUCCESS: Farmer F001 registered. Name: Ramesh Patel
SUCCESS: Commission agent A001 registered. Name: Kisan Seva Kendra
SUCCESS: Commodity C001 (Wheat) registered. MSP: ₹2500. Bidding increment: ₹5
SUCCESS: Trader T001 registered. Credit limit: ₹1000000
SUCCESS: Lot L001 registered. Grade: A. Reference price: ₹2500
SUCCESS: Auction opened for L001. Floor price per quintal: ₹2250.00
SUCCESS: Bid accepted. Lot L001, Trader T001, ₹2300 per quintal
SOLD: Lot L001. Winning trader: T001. Bid: ₹2300 per quintal. Gross value: ₹230000.00. Trader total due including 1% market fee: ₹232300.00
SETTLEMENT SUMMARY: Lot L001 | Farmer Net Payable: ₹228000.00 | Agent Commission: ₹2000.00 | Quality Deductions: ₹0.00 | Market Fee: ₹2300.00
SUCCESS: Settlement finalized for Lot L001.
SETTLEMENT RECORD for Lot L001:
  Farmer ID: F001 | Agent: A001 | Winning Trader: T001
  Declared Weight: 100 q | Actual Weight: 99.5 q
  Winning Bid Price: ₹2300 / q
  Gross Settlement Value: ₹228850.00
  Farmer Quality Deductions: ₹0.00 (Moisture: ₹0.00, Foreign Matter: ₹0.00)
  Agent Commission (2%, max ₹2000): ₹2000.00
  Farmer Net Payable: ₹226850.00
  Market Fee (1% on top): ₹2288.50
  Trader Total Payable: ₹231138.50
SUCCESS: Payment of ₹100000 received from Trader T001 for Lot L001. Remaining dues: ₹131138.50

Registered traders: 1
Registered lots: 1
Auctions opened: 1
```

---

## 12. Implemented Functionalities (Week 2 Checkpoint)

| Requirement Category | Functionality | Status | Implementation Details |
|---|---|---|---|
| **Registration** | Farmer Registration | **Complete** | `Farmer` model in `src/farmer.py`; validates unique non-empty ID and name. |
| **Registration** | Commission Agent Registration | **Complete** | `CommissionAgent` model in `src/agent.py`; validates unique ID and name. |
| **Registration** | Commodity Registration | **Complete** | `Commodity` model in `src/commodity.py`; tracks MSP, quality thresholds, and bidding increments. |
| **Registration** | Trader Registration | **Complete** | `Trader` model in `src/trader.py`; Credit Limit = 10 × Security Deposit. |
| **Lot Management** | Agricultural Lot Registration | **Complete** | `Lot` in `src/lot.py`; validates quantity, MSP, quality parameters; tracks status lifecycle. |
| **Grading** | Automated Grade Calculation | **Complete** | `calculate_grade` in `src/grading.py`; Grade A (M≤12%, FM≤1%, D≤2%), Grade B (M≤14%, FM≤2%, D≤4%), Grade C otherwise. |
| **Pricing** | Reference Price Calculation | **Complete** | `calculate_reference_price` in `src/grading.py`; Grade A = 100% MSP, Grade B = 97% MSP, Grade C = 92% MSP. |
| **Auction** | Timed Auction & Floor Price | **Complete** | `Auction` in `src/auction.py`; initial floor price is 90% of reference price. |
| **Auction** | Bidding Increment Rules | **Complete** | Enforces ₹5 increment for commodities < ₹3,000; ₹10 increment for commodities ≥ ₹3,000. |
| **Auction** | Dynamic Bidding Window & Extensions | **Complete** | 10-minute initial window; 2-minute extension when bid arrives within final 60 seconds (max 3 extensions). |
| **Auction** | Winner & Tie-Breaking | **Complete** | Identifies highest bidder; ties broken by earliest timestamp, then lower trader ID. |
| **Auction** | Unsold Lot Handling | **Complete** | Lots receiving zero valid bids marked `UNSOLD`. |
| **Trader Eligibility** | Exposure & Overdue Restrictions | **Complete** | Checks dues + active winning bids + proposed bid ≤ credit limit; bans traders with dues > 7 days overdue or suspended. |
| **Settlement** | Weigh-Bridge Weigh-In | **Complete** | `WEIGH_IN` command; detects weight variance > 2% allowing withdrawal. |
| **Settlement** | Quality Deductions | **Complete** | Moisture deduction: 1% per point above 12%; Foreign matter: excess % weight deducted before fees. |
| **Settlement** | Fees & Commissions | **Complete** | Market fee: 1% of gross value (paid by trader); Agent commission: 2% of gross value capped at ₹2,000 (deducted from farmer; ₹0 for direct sale). |
| **Settlement** | Net Payable Calculations | **Complete** | Computes farmer net payable and trader total payable using exact `Decimal` precision. |
| **Payment** | Payment Tracking | **Complete** | Tracks payments, remaining dues, deadlines (24h), and overdue penalty calculations. |
| **Command Engine** | Batch File Processing | **Complete** | `process_commands` in `src/main.py`; handles CSV command stream deterministically. |
| **Testing** | Automated Unit Tests | **Complete** | 114 unit tests across all business rules and edge cases; 100% passing. |

---

## 13. Current Implementation Limitations (Scheduled for Week 3+)
To maintain transparency for the Week 2 checkpoint:
1. **Sub-5 Quintal Lot Bundling:** Small lot bundling (BR-39 to BR-41) is designed in the architecture documentation and scheduled for implementation in Week 3.
2. **Multi-Day Re-Auction Simulation Loop:** While `calculate_reauction_floor` and `next_auction_date` are fully implemented and unit-tested in `reauction.py`, multi-day automated cron simulation will be wired into the main loop in Week 3.
3. **Formal Ledger Export Formats:** Outputs are currently formatted and printed via standard output; formal PDF/tabular CSV ledger export will be added in Week 3.
4. **Interactive GUI / Frontend:** By problem statement specification, this is a backend-only engine; no frontend is included.
