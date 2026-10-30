"""
main_window.py - the main application window.

Owns the list of bookings and the BookingStore, builds the sidebar navigation,
switches between pages (welcome -> login -> workspace) and connects the signals
emitted by each page to the actions that must follow.
"""
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QMainWindow, QMessageBox, QPushButton,
                               QStackedWidget, QVBoxLayout, QWidget)

from booking_page import BookingPage
from config import SIDEBAR
from dashboard_page import DashboardPage
from help_page import HelpPage
from intro_page import IntroPage
from login_page import LoginPage
from models import Booking
from pricing import gbp
from rented_cars_page import RentedCarsPage
from storage import BookingStore
from storage_page import StoragePage
from welcome_page import WelcomePage
from widgets import button, label

# Page numbers inside the workspace (same order the pages are added to the stack and the sidebar buttons)
PAGE_DASHBOARD, PAGE_RENTED, PAGE_BOOKING, PAGE_STORAGE, PAGE_HELP = range(5)


class MainWindow(QMainWindow):
    """Top-level window containing the welcome, login and workspace screens."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WeAreCars | Car Rental")
        self.resize(1240, 820)
        self.setMinimumSize(1000, 680)
        # Load saved bookings once; the same list object is shared with the pages that need it
        self.store = BookingStore()
        self.bookings: list[Booking] = self.store.load()

        # Top-level screens in a stack: only one is visible at a time
        self.root = QStackedWidget()
        self.setCentralWidget(self.root)
        self.intro = IntroPage()
        self.welcome, self.login = WelcomePage(), LoginPage()
        self.workspace = self.build_workspace()
        for screen in (self.intro, self.welcome, self.login, self.workspace):
            self.root.addWidget(screen)
        self.intro.finished.connect(lambda: self.root.setCurrentWidget(self.welcome))
        QTimer.singleShot(0, self.intro.start)
        self.welcome.sign_in_requested.connect(lambda: (self.login.reset(), self.root.setCurrentWidget(self.login)))
        self.login.back_requested.connect(lambda: self.root.setCurrentWidget(self.welcome))
        self.login.login_succeeded.connect(self.enter_workspace)

        # Keyboard shortcuts (they only act once the user is signed in)
        QShortcut(QKeySequence("Ctrl+N"), self, lambda: self.goto(PAGE_BOOKING))
        QShortcut(QKeySequence("Ctrl+F"), self, self.focus_search)
        QShortcut(QKeySequence("F1"), self, lambda: self.goto(PAGE_HELP))
        QShortcut(QKeySequence("Ctrl+L"), self, self.sign_out)
        # If the bookings file was corrupt, warn the user shortly after the window appears
        if self.store.load_warning:
            QTimer.singleShot(300, lambda: QMessageBox.warning(self, "Bookings file", self.store.load_warning))

    def build_workspace(self) -> QWidget:
        """Build the signed-in screen: a dark sidebar on the left and a stack of pages on the right."""
        workspace = QWidget()
        workspace_layout = QHBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        # ---- Sidebar ----
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(f"QFrame#sidebar {{ background:{SIDEBAR}; }}")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 26, 18, 20)
        sidebar_layout.setSpacing(4)
        brand_label = label("▣  WEARECARS")
        brand_label.setStyleSheet("color:white; font-weight:800; font-size:14px; letter-spacing:2px; padding:0 8px 22px;")
        sidebar_layout.addWidget(brand_label)
        self.nav_buttons: list[QPushButton] = []
        nav_items = [("Dashboard", "Overview"), ("Rented cars", "All bookings"),
                     ("New booking", "Create a booking (Ctrl+N)"),
                     ("Storage", "Booking file location"), ("Help", "Guidance (F1)")]
        for page_number, (text, tooltip) in enumerate(nav_items):
            nav_button = button(text, "nav", tooltip)
            nav_button.setCheckable(True)
            # `page_number=page_number` binds the current value to each button's lambda
            nav_button.clicked.connect(lambda _checked=False, page_number=page_number: self.goto(page_number))
            self.nav_buttons.append(nav_button)
            sidebar_layout.addWidget(nav_button)
        sidebar_layout.addStretch()
        user_label = label("STA001\nStaff member")
        user_label.setStyleSheet("color:#C9CFC7; padding:8px;")
        sidebar_layout.addWidget(user_label)
        sign_out_button = button("←  Sign out", "ghostdark", "Sign out (Ctrl+L)")
        sign_out_button.clicked.connect(self.sign_out)
        sidebar_layout.addWidget(sign_out_button)
        workspace_layout.addWidget(sidebar)

        # ---- Pages (the order must match the PAGE_* numbers above) ----
        self.pages = QStackedWidget()
        self.dashboard = DashboardPage(self.bookings)
        self.rented = RentedCarsPage(self.bookings, self.store)
        self.booking = BookingPage()
        self.storage = StoragePage(self.store)
        for page in (self.dashboard, self.rented, self.booking, self.storage, HelpPage()):
            self.pages.addWidget(page)
        workspace_layout.addWidget(self.pages, 1)

        # ---- Page signals ----
        self.dashboard.new_booking_requested.connect(lambda: self.goto(PAGE_BOOKING))
        self.dashboard.view_all_requested.connect(lambda: self.goto(PAGE_RENTED))
        self.rented.bookings_changed.connect(self.dashboard.refresh)
        self.booking.booking_saved.connect(self.save_booking)
        self.storage.folder_chosen.connect(self.change_folder)
        return workspace

    def enter_workspace(self) -> None:
        """Called after a successful login: show the workspace on the dashboard."""
        self.root.setCurrentWidget(self.workspace)
        self.goto(PAGE_DASHBOARD)

    def goto(self, page_number: int) -> None:
        """Show one workspace page, highlight its sidebar button and refresh the data pages."""
        if self.root.currentWidget() is not self.workspace:
            return   # ignore shortcuts when not signed in
        self.pages.setCurrentIndex(page_number)
        for index, nav_button in enumerate(self.nav_buttons):
            nav_button.setChecked(index == page_number)
        for page in (self.dashboard, self.rented, self.storage):
            page.refresh()
        if page_number == PAGE_BOOKING:
            self.booking.first_name_edit.setFocus()

    def focus_search(self) -> None:
        """Ctrl+F: open the Rented cars page with the cursor in the search box."""
        if self.root.currentWidget() is self.workspace:
            self.goto(PAGE_RENTED)
            self.rented.search_edit.setFocus()

    def save_booking(self, booking: Booking) -> None:
        """Add a confirmed booking to the list and write it to disk. If saving fails, undo the add."""
        self.bookings.append(booking)
        try:
            self.store.save(self.bookings)
        except OSError as error:
            self.bookings.remove(booking)   # keep memory and file consistent
            QMessageBox.critical(self, "Booking not saved",
                                 f"The booking could not be saved, so nothing was stored.\n\n{error}\n\n"
                                 "Check the storage folder on the Storage page and try again.")
            return
        QMessageBox.information(self, "Booking saved",
                                f"Booking {booking.reference} for {booking.customer} has been saved.\n"
                                f"Total: {gbp(booking.total)}")
        self.booking.reset()
        self.goto(PAGE_RENTED)

    def change_folder(self, folder: Path) -> None:
        """Switch the storage folder, merging in any bookings already stored there."""
        try:
            merged = self.store.change_directory(folder, self.bookings)
        except OSError as error:
            QMessageBox.critical(self, "Could not change folder", str(error))
            return
        self.bookings[:] = merged   # update the shared list in place so every page sees the change
        self.storage.refresh()
        QMessageBox.information(self, "Folder updated", f"Bookings are now stored in:\n{self.store.file}")

    def sign_out(self) -> None:
        """Clear any half-entered booking and return to the welcome screen."""
        if self.root.currentWidget() is self.workspace:
            self.booking.reset()
            self.root.setCurrentWidget(self.welcome)
