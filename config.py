"""
config.py - business rules and theme constants for WeAreCars.

Every price, limit and colour used by the application is defined here, so a
rule (for example the daily rate) only ever has to be changed in one place.

Naming convention used across the project:
    * UPPER_CASE        -> constants
    * snake_case        -> functions, methods, variables and module names
    * PascalCase        -> classes
    * *_edit / *_label / *_button / *_group -> Qt widgets, named after their type
"""

# --------------------------------------------------------------------------------------
# Business rules (taken from the client's specification)
# --------------------------------------------------------------------------------------
# Fixed staff credentials required by the specification.
STAFF_USERNAME = "sta001"
STAFF_PASSWORD = "givemethekeys123"

DAILY_RATE = 25              # GBP per rental day
MILEAGE_PER_DAY = 10         # GBP per day for the "Unlimited mileage" extra
BREAKDOWN_PER_DAY = 2        # GBP per day for the "Breakdown cover" extra
MIN_DAYS, MAX_DAYS = 1, 28   # allowed rental length in days
MIN_AGE, MAX_AGE = 18, 99    # allowed customer age (assumption: 18+ to rent a car)

# Each entry is (name, one-off surcharge in GBP, tooltip text).
CAR_TYPES = [
    ("City car", 0, "Compact and easy to park - ideal for town driving."),
    ("Family car", 50, "Spacious saloon / estate with plenty of boot space."),
    ("Sports car", 75, "High performance two-seater for a special occasion."),
    ("SUV", 65, "Higher driving position with room for luggage and passengers."),
]
FUEL_TYPES = [
    ("Petrol", 0, "Standard petrol engine."),
    ("Diesel", 0, "Efficient on longer journeys."),
    ("Hybrid", 30, "Petrol engine plus electric motor for lower fuel use."),
    ("Full electric", 50, "Zero tailpipe emissions. Charging is the customer's responsibility."),
]

# Quick name -> surcharge lookups used by the pricing code.
CAR_SURCHARGE = {name: surcharge for name, surcharge, _tip in CAR_TYPES}
FUEL_SURCHARGE = {name: surcharge for name, surcharge, _tip in FUEL_TYPES}

# --------------------------------------------------------------------------------------
# Theme colours (hex strings used by the stylesheet and custom painting)
# --------------------------------------------------------------------------------------
INK, SIDEBAR, LIME = "#171A18", "#0D100F", "#BDFC5A"          # text, dark panels, accent
CANVAS, BORDER, MUTED, DANGER = "#F4F5F2", "#E1E5DD", "#6B726C", "#D6333B"
FONT = "Segoe UI"
