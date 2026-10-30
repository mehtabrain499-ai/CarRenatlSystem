"""
pricing.py - price calculation and currency formatting.

Pricing rules (from the specification):
    * Base rate is DAILY_RATE per day.
    * Car type and fuel type surcharges are charged ONCE per rental.
    * Unlimited mileage and breakdown cover are charged PER DAY.
"""
from __future__ import annotations

from config import (BREAKDOWN_PER_DAY, CAR_SURCHARGE, DAILY_RATE, FUEL_SURCHARGE,
                    MILEAGE_PER_DAY)


def price_breakdown(days: int, car: str | None, fuel: str | None,
                    unlimited: bool, breakdown: bool) -> tuple[list[tuple[str, int]], int]:
    """Return (itemised price lines, total price in GBP).

    car and fuel may be None while the user is still choosing; in that case no
    surcharge line is added yet, so the live price panel can update as they go.
    """
    lines = [(f"Car hire  ({days} x £{DAILY_RATE}/day)", days * DAILY_RATE)]
    if car:
        lines.append((f"{car} surcharge", CAR_SURCHARGE[car]))        # one-off
    if fuel:
        lines.append((f"{fuel} surcharge", FUEL_SURCHARGE[fuel]))     # one-off
    if unlimited:
        lines.append((f"Unlimited mileage  ({days} x £{MILEAGE_PER_DAY})", days * MILEAGE_PER_DAY))
    if breakdown:
        lines.append((f"Breakdown cover  ({days} x £{BREAKDOWN_PER_DAY})", days * BREAKDOWN_PER_DAY))
    total = sum(amount for _description, amount in lines)
    return lines, total


def gbp(amount: int) -> str:
    """Format a number as pounds, e.g. 1250 -> '£1,250' (pence only shown if needed)."""
    return f"£{amount:,.2f}" if amount % 1 else f"£{amount:,}"
