"""
dashboard_page.py - the dashboard: key figures, a bookings-by-vehicle chart,
a price guide and the five most recent bookings.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from config import BREAKDOWN_PER_DAY, CAR_TYPES, DAILY_RATE, FUEL_TYPES, MILEAGE_PER_DAY
from models import Booking
from pricing import gbp
from widgets import BarChart, button, card, label, make_table, page_header, scroll_wrap, set_row


class MetricCard(QFrame):
    """A small card showing one headline figure (title, big value, small caption)."""

    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.addWidget(label(title.upper(), "muted"))
        self.value_label = label("–")
        self.value_label.setStyleSheet("font-size:28px; font-weight:800;")
        self.caption_label = label("", "muted")
        layout.addWidget(self.value_label)
        layout.addWidget(self.caption_label)

    def set_values(self, value: str, caption: str = "") -> None:
        """Update the big value and the small caption underneath."""
        self.value_label.setText(value)
        self.caption_label.setText(caption)


class DashboardPage(QWidget):
    """Overview page. `bookings` is the shared list owned by MainWindow."""

    new_booking_requested = Signal()
    view_all_requested = Signal()

    def __init__(self, bookings: list[Booking]) -> None:
        super().__init__()
        self.bookings = bookings
        content = QWidget()
        page_layout = QVBoxLayout(content)
        page_layout.setContentsMargins(36, 30, 36, 30)
        page_layout.setSpacing(18)

        # ---- Header row with the "New booking" button ----
        header_row = QHBoxLayout()
        header_row.addLayout(page_header("Dashboard", "Today's overview of WeAreCars rentals."))
        header_row.addStretch()
        new_booking_button = button("+  New booking", "primary", "Start a new booking (Ctrl+N)")
        new_booking_button.clicked.connect(self.new_booking_requested)
        header_row.addWidget(new_booking_button, 0, Qt.AlignTop)
        page_layout.addLayout(header_row)

        # ---- Four headline figures ----
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(16)
        self.metric_cards = [MetricCard(title) for title in
                             ("Total bookings", "Total revenue", "Average rental", "Most popular")]
        for metric_card in self.metric_cards:
            metrics_row.addWidget(metric_card)
        page_layout.addLayout(metrics_row)

        # ---- Middle row: bar chart (left) and price guide (right) ----
        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)
        chart_card = card()
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(20, 16, 20, 16)
        chart_layout.addWidget(label("Bookings by vehicle type", "h2"))
        self.chart = BarChart()
        chart_layout.addWidget(self.chart)

        guide_card = card()
        guide_layout = QVBoxLayout(guide_card)
        guide_layout.setContentsMargins(20, 16, 20, 16)
        guide_layout.addWidget(label("Price guide", "h2"))
        # Built from config.py so the guide can never disagree with the real prices
        price_guide = label(
            f"<table cellspacing=6><tr><td>Base rate</td><td align=right><b>£{DAILY_RATE}/day</b></td></tr>"
            + "".join(f"<tr><td>{name}</td><td align=right><b>{'–' if surcharge == 0 else '+£' + str(surcharge)}</b></td></tr>"
                      for name, surcharge, _tip in CAR_TYPES)
            + "".join(f"<tr><td>{name}</td><td align=right><b>{'–' if surcharge == 0 else '+£' + str(surcharge)}</b></td></tr>"
                      for name, surcharge, _tip in FUEL_TYPES if surcharge)   # only fuels that cost extra
            + f"<tr><td>Unlimited mileage</td><td align=right><b>+£{MILEAGE_PER_DAY}/day</b></td></tr>"
            f"<tr><td>Breakdown cover</td><td align=right><b>+£{BREAKDOWN_PER_DAY}/day</b></td></tr></table>")
        guide_layout.addWidget(price_guide)
        guide_layout.addStretch()
        middle_row.addWidget(chart_card, 3)
        middle_row.addWidget(guide_card, 2)
        page_layout.addLayout(middle_row)

        # ---- Recent bookings table ----
        recent_card = card()
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(20, 16, 20, 12)
        recent_header = QHBoxLayout()
        recent_header.addWidget(label("Recent bookings", "h2"))
        recent_header.addStretch()
        view_all_button = button("View all →", "link")
        view_all_button.clicked.connect(self.view_all_requested)
        recent_header.addWidget(view_all_button)
        recent_layout.addLayout(recent_header)
        self.table = make_table(["Reference", "Customer", "Vehicle", "Days", "Total"])
        self.table.setMinimumHeight(5 * 44 + 40)
        recent_layout.addWidget(self.table)
        page_layout.addWidget(recent_card)
        page_layout.addStretch()

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_wrap(content))

    def refresh(self) -> None:
        """Recalculate every figure, the chart and the table from the current bookings."""
        bookings = self.bookings
        booking_count, revenue = len(bookings), sum(booking.total for booking in bookings)
        self.metric_cards[0].set_values(str(booking_count), "since records began")
        self.metric_cards[1].set_values(gbp(revenue), "all bookings")
        average_days = sum(booking.days for booking in bookings) / booking_count if booking_count else 0
        self.metric_cards[2].set_values(f"{average_days:.1f} days" if booking_count else "–", "per booking")
        # Count bookings per vehicle type and find the most popular one
        counts = {name: sum(1 for booking in bookings if booking.car_type == name) for name, _s, _t in CAR_TYPES}
        most_popular = max(counts, key=counts.get) if booking_count else "–"
        self.metric_cards[3].set_values(most_popular,
                                        f"{counts.get(most_popular, 0)} booking(s)" if booking_count else "no data yet")
        self.chart.set_data(list(counts.items()))
        # Show the five newest bookings
        recent = sorted(bookings, key=lambda booking: booking.booked_at, reverse=True)[:5]
        self.table.setRowCount(len(recent))
        for row, booking in enumerate(recent):
            set_row(self.table, row, [(booking.reference, booking.reference),
                                      (booking.customer, booking.customer.lower()),
                                      (booking.car_type, booking.car_type), (str(booking.days), booking.days),
                                      (gbp(booking.total), booking.total)], (3, 4))
