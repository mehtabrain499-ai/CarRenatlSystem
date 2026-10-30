"""
booking_page.py - the main booking area.

Staff enter the customer and rental details, a live price panel updates as they
go, and "Review booking" opens a summary dialog before the booking is saved.
Mandatory fields are marked * and validated with inline error messages.
"""
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QDialog, QFrame, QGridLayout, QHBoxLayout, QLineEdit, QMessageBox,
                               QVBoxLayout, QWidget)

from config import (BREAKDOWN_PER_DAY, CAR_TYPES, DAILY_RATE, DANGER, FUEL_TYPES, LIME, MAX_AGE,
                    MAX_DAYS, MILEAGE_PER_DAY, MIN_AGE, MIN_DAYS, SIDEBAR)
from dialogs import SummaryDialog
from models import Booking
from pricing import gbp, price_breakdown
from validation import validate_address, validate_age, validate_days, validate_name
from widgets import DaysInput, Field, OptionGroup, button, card, label, page_header, scroll_wrap


class BookingPage(QWidget):
    """The new-booking form (left) and live price summary (right)."""

    booking_saved = Signal(Booking)   # emitted when staff confirm the summary; MainWindow stores it

    def __init__(self) -> None:
        super().__init__()
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        form_content = QWidget()
        form_layout = QVBoxLayout(form_content)
        form_layout.setContentsMargins(36, 30, 24, 30)
        form_layout.setSpacing(18)
        form_layout.addLayout(page_header("New booking", "Fields marked with * are mandatory. The price updates as you go."))

        # ---- Customer section ----
        customer_card = card()
        customer_grid = QGridLayout(customer_card)
        customer_grid.setContentsMargins(22, 18, 22, 20)
        customer_grid.setHorizontalSpacing(16)
        customer_grid.setVerticalSpacing(12)
        customer_grid.addWidget(label("Customer", "h2"), 0, 0, 1, 2)
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("e.g. Jane")
        self.first_name_edit.setMaxLength(40)
        self.surname_edit = QLineEdit()
        self.surname_edit.setPlaceholderText("e.g. Smith")
        self.surname_edit.setMaxLength(40)
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("e.g. 12 High Street, Sunderland, SR1 3AB")
        self.address_edit.setMaxLength(120)
        self.age_edit = QLineEdit()
        self.age_edit.setPlaceholderText("e.g. 25")
        self.age_edit.setMaxLength(3)
        self.licence_group = OptionGroup([("Yes", "Valid full licence held", "The customer holds a valid driving licence."),
                                          ("No", "No valid licence", "Bookings cannot proceed without a valid licence.")])
        # self.fields maps a field key to its Field wrapper (label, input, error message)
        self.fields = {
            "first": Field("First name", self.first_name_edit, tip="Letters, spaces, hyphens and apostrophes only."),
            "last": Field("Surname", self.surname_edit, tip="Letters, spaces, hyphens and apostrophes only."),
            "address": Field("Address", self.address_edit, tip="Full postal address including town or postcode."),
            "age": Field("Age", self.age_edit, hint=f"Customers must be {MIN_AGE} or over.",
                         tip=f"Whole number, {MIN_AGE}–{MAX_AGE}."),
            "licence": Field("Valid driving licence", self.licence_group, tip="Ask to see the customer's licence."),
        }
        customer_grid.addWidget(self.fields["first"], 1, 0)
        customer_grid.addWidget(self.fields["last"], 1, 1)
        customer_grid.addWidget(self.fields["address"], 2, 0, 1, 2)
        customer_grid.addWidget(self.fields["age"], 3, 0, 1, 2)
        customer_grid.addWidget(self.fields["licence"], 4, 0, 1, 2)
        # Red banner shown when the answer to "valid licence" is No
        self.licence_banner = label("⚠  A valid driving licence is required. This booking cannot proceed.", "error", wrap=True)
        self.licence_banner.setStyleSheet(
            f"background:#FDECEC; color:{DANGER}; border-radius:8px; padding:10px 12px; font-weight:600;")
        self.licence_banner.hide()
        customer_grid.addWidget(self.licence_banner, 5, 0, 1, 2)
        form_layout.addWidget(customer_card)

        # ---- Rental section ----
        rental_card = card()
        rental_layout = QVBoxLayout(rental_card)
        rental_layout.setContentsMargins(22, 18, 22, 20)
        rental_layout.setSpacing(14)
        rental_layout.addWidget(label("Rental", "h2"))
        self.days_input = DaysInput()
        # Options are built from config.py so prices shown always match the pricing rules
        self.car_group = OptionGroup([(name, "No extra charge" if surcharge == 0 else f"+ £{surcharge}", tip)
                                      for name, surcharge, tip in CAR_TYPES])
        self.fuel_group = OptionGroup([(name, "No extra charge" if surcharge == 0 else f"+ £{surcharge}", tip)
                                       for name, surcharge, tip in FUEL_TYPES])
        self.extras_group = OptionGroup([("Unlimited mileage", f"+ £{MILEAGE_PER_DAY} per day", "Drive as far as you like."),
                                         ("Breakdown cover", f"+ £{BREAKDOWN_PER_DAY} per day",
                                          "Roadside assistance for the rental period.")],
                                        multi=True)
        self.fields["days"] = Field("Number of days", self.days_input,
                                    tip=f"{MIN_DAYS}–{MAX_DAYS} days at £{DAILY_RATE} per day.")
        self.fields["car"] = Field("Type of car", self.car_group)
        self.fields["fuel"] = Field("Fuel type", self.fuel_group)
        rental_layout.addWidget(self.fields["days"])
        rental_layout.addWidget(self.fields["car"])
        rental_layout.addWidget(self.fields["fuel"])
        rental_layout.addWidget(Field("Optional extras", self.extras_group, required=False))
        form_layout.addWidget(rental_card)
        form_layout.addStretch()
        outer_layout.addWidget(scroll_wrap(form_content), 1)

        # ---- Live price panel (dark column on the right) ----
        price_panel = QFrame()
        price_panel.setFixedWidth(340)
        price_panel.setStyleSheet(f"QFrame#side {{ background:{SIDEBAR}; }} QLabel {{ color:white; }}")
        price_panel.setObjectName("side")
        panel_layout = QVBoxLayout(price_panel)
        panel_layout.setContentsMargins(26, 30, 26, 26)
        panel_layout.setSpacing(8)
        panel_title = label("PRICE SUMMARY")
        panel_title.setStyleSheet(f"color:{LIME}; font-weight:700; letter-spacing:2px; font-size:11px;")
        panel_layout.addWidget(panel_title)
        self.price_lines_layout = QVBoxLayout()   # itemised price lines are added here by update_price()
        self.price_lines_layout.setSpacing(6)
        panel_layout.addLayout(self.price_lines_layout)
        panel_layout.addStretch()
        self.total_label = label("£25")
        self.total_label.setStyleSheet("color:white; font-size:40px; font-weight:800;")
        total_caption = label("Estimated total")
        total_caption.setStyleSheet("color:#8E968C;")
        panel_layout.addWidget(total_caption)
        panel_layout.addWidget(self.total_label)
        panel_layout.addSpacing(8)
        self.review_button = button("Review booking  →", "lime", "Check the details before saving (Ctrl+Enter)")
        self.review_button.setMinimumHeight(48)
        clear_button = button("Clear form", "ghostdark", "Reset every field")
        panel_layout.addWidget(self.review_button)
        panel_layout.addWidget(clear_button)
        outer_layout.addWidget(price_panel)

        # ---- Wiring ----
        # Fields the user has already visited. Errors only show for these, so a blank form isn't covered in red.
        self.touched: set[str] = set()
        text_inputs = (("first", self.first_name_edit), ("last", self.surname_edit),
                       ("address", self.address_edit), ("age", self.age_edit))
        for key, text_input in text_inputs:
            # `key=key` binds the current key to each lambda (otherwise they would all use the last key)
            text_input.textChanged.connect(lambda _text=None, key=key: self.on_text_changed(key))
            text_input.editingFinished.connect(lambda key=key: self.on_editing_finished(key))
        self.days_input.textChanged.connect(lambda _text=None: self.on_text_changed("days"))
        self.days_input.editingFinished.connect(lambda: self.on_editing_finished("days"))
        for key, option_group in (("licence", self.licence_group), ("car", self.car_group), ("fuel", self.fuel_group)):
            option_group.selection_changed.connect(lambda key=key: self.on_editing_finished(key))
        self.extras_group.selection_changed.connect(self.update_price)
        self.review_button.clicked.connect(self.start_review)
        clear_button.clicked.connect(self.reset)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.start_review)
        self.update_price()

    # ----------------------------------------------------------------------------------
    # Validation
    # ----------------------------------------------------------------------------------
    def error_message_for(self, key: str) -> str:
        """Return the current error message for one field ("" if it is valid)."""
        checks = {
            "first": lambda: validate_name(self.first_name_edit.text(), "First name"),
            "last": lambda: validate_name(self.surname_edit.text(), "Surname"),
            "address": lambda: validate_address(self.address_edit.text()),
            "age": lambda: validate_age(self.age_edit.text()),
            "days": lambda: validate_days(self.days_input.text()),
            "licence": lambda: "" if self.licence_group.value() == "Yes" else
            ("Please confirm whether the customer holds a valid licence." if self.licence_group.value() is None else
             "A valid driving licence is required to rent a car."),
            "car": lambda: "" if self.car_group.value() else "Please choose a type of car.",
            "fuel": lambda: "" if self.fuel_group.value() else "Please choose a fuel type.",
        }
        return checks[key]()

    def validate_field(self, key: str) -> bool:
        """Validate one field, show/hide its error, and return True if it is valid."""
        error = self.error_message_for(key)
        self.fields[key].set_error(error)
        if key == "licence":
            # Answering "No" shows the red banner and blocks the Review button.
            self.licence_banner.setVisible(self.licence_group.value() == "No")
            self.review_button.setEnabled(self.licence_group.value() != "No")
        return not error

    def on_text_changed(self, key: str) -> None:
        """Re-validate as the user types, but only for fields they have already visited."""
        if key in self.touched:
            self.validate_field(key)
        if key == "days":
            self.update_price()

    def on_editing_finished(self, key: str) -> None:
        """The user left the field (or picked an option): mark it visited and validate it."""
        self.touched.add(key)
        self.validate_field(key)
        self.update_price()

    # ----------------------------------------------------------------------------------
    # Live price panel
    # ----------------------------------------------------------------------------------
    def update_price(self) -> None:
        """Rebuild the itemised price lines and the total from the current form values."""
        # Remove the old lines first
        while self.price_lines_layout.count():
            item = self.price_lines_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Only price a valid number of days; otherwise show a prompt and a dash
        try:
            days = int(self.days_input.text())
            days = days if MIN_DAYS <= days <= MAX_DAYS else 0
        except ValueError:
            days = 0
        if not days:
            self.add_price_line("Enter a valid number of days", "")
            self.total_label.setText("–")
            return
        lines, total = price_breakdown(days, self.car_group.value(), self.fuel_group.value(),
                                       self.extras_group.checked("Unlimited mileage"),
                                       self.extras_group.checked("Breakdown cover"))
        for description, amount in lines:
            self.add_price_line(description, gbp(amount))
        if not self.car_group.value() or not self.fuel_group.value():
            self.add_price_line("Select car and fuel type to complete", "")
        self.total_label.setText(gbp(total))

    def add_price_line(self, description: str, amount_text: str) -> None:
        """Add one row (description on the left, amount on the right) to the price panel."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        description_label, amount_label = label(description, wrap=True), label(amount_text)
        description_label.setStyleSheet("color:#C9CFC7;")
        amount_label.setStyleSheet("color:white; font-weight:700;")
        row_layout.addWidget(description_label, 1)
        row_layout.addWidget(amount_label)
        self.price_lines_layout.addWidget(row_widget)

    # ----------------------------------------------------------------------------------
    # Actions
    # ----------------------------------------------------------------------------------
    def start_review(self) -> None:
        """Validate the whole form; if valid, show the summary dialog and emit booking_saved on confirm."""
        # Each entry is (field key, widget to focus if invalid). None means "focus the Field wrapper".
        fields_in_order = [("first", self.first_name_edit), ("last", self.surname_edit),
                           ("address", self.address_edit), ("age", self.age_edit), ("licence", None),
                           ("days", self.days_input.edit), ("car", None), ("fuel", None)]
        invalid_fields = [(key, widget) for key, widget in fields_in_order if not self.validate_field(key)]
        if invalid_fields:
            first_key, first_widget = invalid_fields[0]
            (first_widget or self.fields[first_key]).setFocus()   # jump to the first problem
            QMessageBox.warning(self, "Please check the form",
                                f"{len(invalid_fields)} field(s) need attention. "
                                "Messages are shown in red beside each field.")
            return
        # All valid: build the booking, including the final calculated total
        unlimited_mileage = self.extras_group.checked("Unlimited mileage")
        breakdown_cover = self.extras_group.checked("Breakdown cover")
        _lines, total = price_breakdown(int(self.days_input.text()), self.car_group.value(),
                                        self.fuel_group.value(), unlimited_mileage, breakdown_cover)
        booking = Booking(first_name=self.first_name_edit.text().strip(), surname=self.surname_edit.text().strip(),
                          address=" ".join(self.address_edit.text().split()),   # tidy repeated spaces
                          age=int(self.age_edit.text()), days=int(self.days_input.text()),
                          car_type=self.car_group.value(), fuel_type=self.fuel_group.value(),
                          unlimited_mileage=unlimited_mileage, breakdown_cover=breakdown_cover, total=total)
        # Summary screen: only store the booking if the staff member confirms it
        if SummaryDialog(booking, self.window(), confirm=True).exec() == QDialog.Accepted:
            self.booking_saved.emit(booking)

    def reset(self) -> None:
        """Clear every field, error message and selection, ready for the next booking."""
        self.touched.clear()
        for text_input in (self.first_name_edit, self.surname_edit, self.address_edit, self.age_edit):
            text_input.clear()
        self.days_input.edit.setText("1")
        for option_group in (self.licence_group, self.car_group, self.fuel_group, self.extras_group):
            option_group.reset()
        for field in self.fields.values():
            field.set_error("", True)
        self.licence_banner.hide()
        self.review_button.setEnabled(True)
        self.update_price()
        self.first_name_edit.setFocus()
