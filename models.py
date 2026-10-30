"""
models.py - the domain model.

A Booking is one saved car rental. It is a dataclass so it can be converted to a
plain dictionary (dataclasses.asdict) and saved as JSON by storage.py.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Booking:
    """A single car rental booking, as entered by staff and stored on disk."""

    # --- Customer details ---
    first_name: str
    surname: str
    address: str
    age: int
    # --- Rental details ---
    days: int
    car_type: str
    fuel_type: str
    unlimited_mileage: bool = False
    breakdown_cover: bool = False
    total: int = 0  # final price in GBP, calculated by pricing.price_breakdown()
    # --- Generated automatically ---
    # Short unique reference such as "WAC-1A2B3C".
    reference: str = field(default_factory=lambda: "WAC-" + uuid.uuid4().hex[:6].upper())
    # ISO timestamp of when the booking was created.
    booked_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def customer(self) -> str:
        """Full customer name, e.g. 'Jane Smith'."""
        return f"{self.first_name} {self.surname}"

    @property
    def extras(self) -> str:
        """Comma-separated list of chosen optional extras, or 'None'."""
        chosen_extras = [name for name, selected in (("Unlimited mileage", self.unlimited_mileage),
                                                     ("Breakdown cover", self.breakdown_cover)) if selected]
        return ", ".join(chosen_extras) if chosen_extras else "None"

    @property
    def booked_dt(self) -> datetime:
        """The booking time as a datetime object (the file stores it as text)."""
        return datetime.fromisoformat(self.booked_at)
