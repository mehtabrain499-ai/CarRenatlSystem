"""
dialogs.py - pop-up windows.

SummaryDialog is used twice: as the "Confirm booking details" screen before a
booking is saved, and as a read-only "Booking details" view from the Rented cars page.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from models import Booking
from pricing import gbp, price_breakdown
from widgets import button, card, label


class SummaryDialog(QDialog):
    """Booking summary. confirm=True shows Confirm/Back buttons; otherwise a read-only Close."""

    def __init__(self, booking: Booking, parent: QWidget, confirm: bool) -> None:
        super().__init__(parent)
        self.setWindowTitle("Review booking" if confirm else f"Booking {booking.reference}")
        self.setMinimumWidth(520)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(26, 22, 26, 22)
        root_layout.setSpacing(14)
        root_layout.addWidget(label("Confirm booking details" if confirm else "Booking details", "h1"))
        root_layout.addWidget(label("Please check everything below with the customer before saving." if confirm
                                    else f"Reference {booking.reference}  ·  booked {booking.booked_dt:%d %b %Y, %H:%M}",
                                    "muted"))

        def add_section(title: str, rows: list[tuple[str, str]], bold_last_row: bool = False) -> None:
            """Add a titled card containing (name, value) rows; the last row can be emphasised (the total)."""
            section_card = card()
            grid = QGridLayout(section_card)
            grid.setContentsMargins(18, 14, 18, 14)
            grid.setVerticalSpacing(7)
            grid.addWidget(label(title, "h2"), 0, 0, 1, 2)
            for row_number, (name, value) in enumerate(rows, 1):
                is_emphasised = bold_last_row and row_number == len(rows)
                name_label = label(name, "" if is_emphasised else "muted")
                value_label = label(value, wrap=True)
                value_label.setAlignment(Qt.AlignRight)
                if is_emphasised:
                    name_label.setStyleSheet("font-weight:800; font-size:15px;")
                    value_label.setStyleSheet("font-weight:800; font-size:18px;")
                grid.addWidget(name_label, row_number, 0)
                grid.addWidget(value_label, row_number, 1)
            grid.setColumnStretch(0, 1)
            root_layout.addWidget(section_card)

        add_section("Customer", [("Name", booking.customer), ("Address", booking.address), ("Age", str(booking.age)),
                                 ("Driving licence", "Confirmed valid")])
        add_section("Rental", [("Duration", f"{booking.days} day(s)"), ("Vehicle", booking.car_type),
                               ("Fuel", booking.fuel_type), ("Optional extras", booking.extras)])
        # Recalculate the price so the summary always matches the pricing rules.
        price_lines, total = price_breakdown(booking.days, booking.car_type, booking.fuel_type,
                                             booking.unlimited_mileage, booking.breakdown_cover)
        add_section("Price", [(description, gbp(amount)) for description, amount in price_lines]
                    + [("TOTAL", gbp(total))], bold_last_row=True)

        # Button row, right-aligned
        button_row = QHBoxLayout()
        button_row.addStretch()
        if confirm:
            back_button = button("Back to booking", "ghost")
            back_button.clicked.connect(self.reject)       # reject() closes the dialog as "cancelled"
            confirm_button = button("Confirm & save booking", "primary")
            confirm_button.setDefault(True)
            confirm_button.clicked.connect(self.accept)    # accept() closes the dialog as "confirmed"
            button_row.addWidget(back_button)
            button_row.addWidget(confirm_button)
        else:
            close_button = button("Close", "primary")
            close_button.clicked.connect(self.accept)
            button_row.addWidget(close_button)
        root_layout.addLayout(button_row)
