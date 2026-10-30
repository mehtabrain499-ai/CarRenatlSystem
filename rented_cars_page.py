"""
rented_cars_page.py - the list of rented cars.

Lets staff search and filter every booking, open the full details, cancel a
booking, and export the visible list to a CSV file.
"""
import csv

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QLineEdit, QMessageBox,
                               QVBoxLayout, QWidget)

from config import CAR_TYPES
from dialogs import SummaryDialog
from models import Booking
from pricing import gbp
from storage import BookingStore
from widgets import button, card, label, make_table, page_header, set_row


class RentedCarsPage(QWidget):
    """Searchable table of bookings. `bookings` is the shared list owned by MainWindow."""

    bookings_changed = Signal()   # emitted after a booking is cancelled so other pages can refresh

    def __init__(self, bookings: list[Booking], store: BookingStore) -> None:
        super().__init__()
        self.bookings, self.store = bookings, store
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(36, 30, 36, 30)
        page_layout.setSpacing(16)
        page_layout.addLayout(page_header("Rented cars", "Every booking on record. Double-click a row for full details."))

        # ---- Search box, vehicle filter and export button ----
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search customer, reference, vehicle, fuel or address…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setToolTip("Search bookings (Ctrl+F)")
        self.vehicle_filter = QComboBox()
        self.vehicle_filter.addItems(["All vehicles"] + [name for name, _surcharge, _tip in CAR_TYPES])
        self.vehicle_filter.setToolTip("Filter by vehicle type")
        self.vehicle_filter.setMinimumWidth(160)
        export_button = button("Export CSV", "ghost", "Save the list shown to a CSV file")
        toolbar.addWidget(self.search_edit, 1)
        toolbar.addWidget(self.vehicle_filter)
        toolbar.addWidget(export_button)
        page_layout.addLayout(toolbar)

        # ---- Bookings table (with an "empty" message shown instead when there are no rows) ----
        table_card = card()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(6, 6, 6, 6)
        self.table = make_table(["Reference", "Booked", "Customer", "Vehicle", "Fuel", "Days", "Extras", "Total"])
        self.table.setSortingEnabled(True)   # click a column heading to sort
        table_layout.addWidget(self.table)
        self.empty_label = label("", "muted")
        self.empty_label.setAlignment(Qt.AlignCenter)
        table_layout.addWidget(self.empty_label)
        page_layout.addWidget(table_card, 1)

        # ---- Footer: count/total on the left, action buttons on the right ----
        footer_row = QHBoxLayout()
        self.count_label = label("", "muted")
        self.view_button = button("View details", "ghost")
        self.cancel_button = button("Cancel booking", "danger", "Permanently remove the selected booking")
        footer_row.addWidget(self.count_label)
        footer_row.addStretch()
        footer_row.addWidget(self.view_button)
        footer_row.addWidget(self.cancel_button)
        page_layout.addLayout(footer_row)

        # ---- Wiring ----
        self.search_edit.textChanged.connect(self.refresh)
        self.vehicle_filter.currentIndexChanged.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.cellDoubleClicked.connect(lambda *_args: self.show_details())
        self.view_button.clicked.connect(self.show_details)
        self.cancel_button.clicked.connect(self.cancel_booking)
        export_button.clicked.connect(self.export_csv)
        self.on_selection_changed()

    def visible_bookings(self) -> list[Booking]:
        """Bookings matching the search text and vehicle filter, newest first."""
        search_text, vehicle = self.search_edit.text().strip().lower(), self.vehicle_filter.currentText()
        matches = []
        for booking in self.bookings:
            # One searchable string per booking so a single box searches every column
            searchable = (f"{booking.reference} {booking.customer} {booking.address} "
                          f"{booking.car_type} {booking.fuel_type} {booking.extras}").lower()
            if search_text in searchable and vehicle in ("All vehicles", booking.car_type):
                matches.append(booking)
        return sorted(matches, key=lambda booking: booking.booked_at, reverse=True)

    def refresh(self) -> None:
        """Rebuild the table from the current search/filter and update the footer."""
        rows = self.visible_bookings()
        self.table.setSortingEnabled(False)   # sorting must be off while rows are being filled in
        self.table.setRowCount(len(rows))
        for row, booking in enumerate(rows):
            set_row(self.table, row, [(booking.reference, booking.reference),
                                      (f"{booking.booked_dt:%d %b %Y}", booking.booked_at),
                                      (booking.customer, booking.customer.lower()),
                                      (booking.car_type, booking.car_type), (booking.fuel_type, booking.fuel_type),
                                      (str(booking.days), booking.days), (booking.extras, booking.extras),
                                      (gbp(booking.total), booking.total)], (5, 7))
        self.table.setSortingEnabled(True)
        shown_total = sum(booking.total for booking in rows)
        self.count_label.setText(f"{len(rows)} booking(s)  ·  {gbp(shown_total)} total")
        if rows:
            self.empty_label.hide()
            self.table.show()
        else:
            # Different message depending on whether there are no bookings at all or just no matches
            self.table.hide()
            self.empty_label.setText("No bookings match your search." if self.bookings else
                                     "No cars have been rented yet.\nCreate the first booking from “New booking”.")
            self.empty_label.setMinimumHeight(200)
            self.empty_label.show()
        self.on_selection_changed()

    def selected_booking(self) -> Booking | None:
        """The booking for the selected table row, or None if nothing is selected."""
        row = self.table.currentRow()
        if row < 0 or not self.table.item(row, 0):
            return None
        reference = self.table.item(row, 0).text()   # column 0 holds the unique reference
        return next((booking for booking in self.bookings if booking.reference == reference), None)

    def on_selection_changed(self) -> None:
        """Enable the View/Cancel buttons only when a row is selected."""
        has_selection = self.selected_booking() is not None
        self.view_button.setEnabled(has_selection)
        self.cancel_button.setEnabled(has_selection)

    def show_details(self) -> None:
        """Open the read-only summary of the selected booking."""
        booking = self.selected_booking()
        if booking:
            SummaryDialog(booking, self.window(), confirm=False).exec()

    def cancel_booking(self) -> None:
        """Ask for confirmation, then permanently remove the selected booking."""
        booking = self.selected_booking()
        if not booking:
            return
        answer = QMessageBox.question(self, "Cancel booking",
                                      f"Remove booking {booking.reference} for {booking.customer}?\n"
                                      "This cannot be undone.",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.bookings.remove(booking)
            try:
                self.store.save(self.bookings)
            except OSError as error:
                QMessageBox.critical(self, "Could not save", f"The change could not be saved:\n{error}")
            self.bookings_changed.emit()
            self.refresh()

    def export_csv(self) -> None:
        """Save the bookings currently shown to a CSV file chosen by the user."""
        rows = self.visible_bookings()
        if not rows:
            QMessageBox.information(self, "Nothing to export", "There are no bookings in the current list.")
            return
        path, _selected_filter = QFileDialog.getSaveFileName(self, "Export bookings", "wearecars_bookings.csv",
                                                             "CSV files (*.csv)")
        if not path:
            return   # user cancelled the file dialog
        try:
            # utf-8-sig adds a byte-order mark so Excel opens the £ and accented characters correctly
            with open(path, "w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Reference", "Booked", "First name", "Surname", "Address", "Age", "Days", "Vehicle",
                                 "Fuel", "Unlimited mileage", "Breakdown cover", "Total (GBP)"])
                for booking in rows:
                    writer.writerow([booking.reference, booking.booked_at, booking.first_name, booking.surname,
                                     booking.address, booking.age, booking.days, booking.car_type,
                                     booking.fuel_type, booking.unlimited_mileage, booking.breakdown_cover,
                                     booking.total])
        except OSError as error:
            QMessageBox.critical(self, "Export failed", str(error))
