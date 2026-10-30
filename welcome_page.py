"""
welcome_page.py - the welcome splash screen.

Shows a welcome message, brief instructions on how to use the system, and a
button (or the Enter key) that continues to the staff login page.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from config import INK, LIME, SIDEBAR
from widgets import WelcomeArtwork, button, label


class WelcomePage(QWidget):
    """Splash page: rental instructions beside an animated car illustration."""

    sign_in_requested = Signal()   # emitted when the user wants to go to the login page

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("welcome")
        self.setAttribute(Qt.WA_StyledBackground, True)   # lets the stylesheet paint this page's background
        self.setStyleSheet(f"QWidget#welcome {{ background:{SIDEBAR}; }}")
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---- Left column: brand, heading, numbered instructions, sign-in button ----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(64, 48, 40, 48)
        left_layout.setSpacing(0)
        brand_label = label("▣  WEARECARS")
        brand_label.setStyleSheet("color:white; font-weight:800; font-size:15px; letter-spacing:2px;")
        left_layout.addWidget(brand_label)
        left_layout.addStretch(2)
        eyebrow_label = label("SUNDERLAND · CAR RENTAL")
        eyebrow_label.setStyleSheet(f"color:{LIME}; font-weight:700; letter-spacing:2px; font-size:12px;")
        left_layout.addWidget(eyebrow_label)
        title_label = label("Welcome to\nWeAreCars.")
        title_label.setStyleSheet("color:white; font-size:48px; font-weight:800; line-height:1.1;")
        left_layout.addWidget(title_label)
        intro_label = label("Quick, accurate rental bookings with clear pricing. Here is how to get started:", wrap=True)
        intro_label.setStyleSheet("color:#A9B0A8; font-size:15px; margin-top:8px;")
        left_layout.addWidget(intro_label)
        left_layout.addSpacing(18)

        # The four getting-started steps, each shown as a numbered circle with a title and description
        steps = [
            ("Sign in", "Use your staff username and password."),
            ("Check rented cars", "See current bookings and search by customer or vehicle."),
            ("Create a booking", "Enter details, pick options and watch the price update live."),
            ("Review & confirm", "Check the summary with the customer, then save."),
        ]
        for step_number, (step_title, step_description) in enumerate(steps, 1):
            step_row = QHBoxLayout()
            step_row.setSpacing(14)
            number_label = label(str(step_number))
            number_label.setFixedSize(30, 30)
            number_label.setAlignment(Qt.AlignCenter)
            number_label.setStyleSheet(f"background:{LIME}; color:{INK}; border-radius:15px; font-weight:800;")
            text_column = QVBoxLayout()
            text_column.setSpacing(0)
            step_title_label = label(step_title)
            step_title_label.setStyleSheet("color:white; font-weight:700; font-size:14px;")
            step_description_label = label(step_description, wrap=True)
            step_description_label.setStyleSheet("color:#8E968C; font-size:12px;")
            text_column.addWidget(step_title_label)
            text_column.addWidget(step_description_label)
            step_row.addWidget(number_label, 0, Qt.AlignTop)
            step_row.addLayout(text_column)
            left_layout.addLayout(step_row)
            left_layout.addSpacing(10)

        left_layout.addSpacing(14)
        sign_in_button = button("Staff sign in  →", "lime", "Continue to the staff login (Enter)")
        sign_in_button.setMinimumHeight(48)
        sign_in_button.setMaximumWidth(240)
        sign_in_button.clicked.connect(self.sign_in_requested)
        left_layout.addWidget(sign_in_button)
        left_layout.addStretch(3)
        footer_label = label("£25 per day  ·  1–28 day rentals  ·  4 vehicle types  ·  4 fuel options", wrap=True)
        footer_label.setStyleSheet("color:#6E756D; font-size:12px;")
        left_layout.addWidget(footer_label)

        # ---- Right column: continuously animated car illustration ----
        root_layout.addWidget(left_panel, 5)
        self.artwork = WelcomeArtwork()
        root_layout.addWidget(self.artwork, 4)
        QShortcut(QKeySequence(Qt.Key_Return), self, self.sign_in_requested)   # Enter key shortcut
