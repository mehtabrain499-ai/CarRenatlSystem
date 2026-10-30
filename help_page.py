"""
help_page.py - the Help page: how to make a booking, the business rules and
the keyboard shortcuts. Numbers come from config.py so the text never goes out of date.
"""
from PySide6.QtWidgets import QVBoxLayout, QWidget

from config import BREAKDOWN_PER_DAY, MAX_DAYS, MILEAGE_PER_DAY, MIN_AGE, MIN_DAYS
from widgets import card, label, page_header, scroll_wrap


class HelpPage(QWidget):
    """Static guidance for staff, shown as three cards."""

    def __init__(self) -> None:
        super().__init__()
        content = QWidget()
        page_layout = QVBoxLayout(content)
        page_layout.setContentsMargins(36, 30, 36, 30)
        page_layout.setSpacing(16)
        page_layout.addLayout(page_header("Help", "Quick guidance for staff."))

        def add_block(title: str, html_text: str) -> None:
            """Add one help card with a heading and rich-text (HTML) body."""
            block_card = card()
            block_layout = QVBoxLayout(block_card)
            block_layout.setContentsMargins(22, 18, 22, 18)
            block_layout.addWidget(label(title, "h2"))
            block_layout.addWidget(label(html_text, wrap=True))
            page_layout.addWidget(block_card)

        add_block("Making a booking",
                  "1. Open <b>New booking</b> (Ctrl+N).<br>2. Complete every field marked "
                  "<span style='color:#D6333B'>*</span>. Problems are explained under the field in red.<br>"
                  "3. Hover over the <b>?</b> icons or any option for tips.<br>"
                  "4. Click <b>Review booking</b>, check the summary with the customer and press "
                  "<b>Confirm &amp; save</b>.")
        add_block("Rules",
                  "• Customers must hold a valid driving licence — otherwise the booking cannot proceed.<br>"
                  f"• Minimum age {MIN_AGE}. Rentals last {MIN_DAYS}–{MAX_DAYS} days.<br>"
                  f"• Vehicle and fuel surcharges are charged once per rental. Unlimited mileage (£{MILEAGE_PER_DAY}) "
                  f"and breakdown cover (£{BREAKDOWN_PER_DAY}) are charged per day.")
        add_block("Keyboard shortcuts",
                  "Ctrl+N new booking &nbsp;·&nbsp; Ctrl+Enter review booking &nbsp;·&nbsp; Ctrl+F search rented cars "
                  "&nbsp;·&nbsp; F1 this page &nbsp;·&nbsp; Ctrl+L sign out")
        page_layout.addStretch()
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_wrap(content))
