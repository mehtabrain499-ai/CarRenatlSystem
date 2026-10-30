"""
login_page.py - the staff login page.

Checks the typed username and password against the fixed staff credentials in
config.py. After MAX_ATTEMPTS wrong tries the form is locked for LOCK_SECONDS.
"""
from math import ceil
import hmac
import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from config import SIDEBAR, STAFF_PASSWORD, STAFF_USERNAME
from widgets import Field, Hero, button, card, label, repolish


class LoginPage(QWidget):
    """Login form with inline validation, show/hide password and a lockout after repeated failures."""

    login_succeeded = Signal()   # emitted when the credentials are correct
    back_requested = Signal()    # emitted when the user clicks "Back to welcome"
    MAX_ATTEMPTS, LOCK_SECONDS = 5, 30

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("loginpage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"QWidget#loginpage {{ background:{SIDEBAR}; }}")
        self.failed_attempts = 0
        self.locked_until = 0.0     # time.time() value until which sign-in is blocked

        # Keep the car photo and sign-in form side by side on the login screen.
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.hero = Hero()
        root_layout.addWidget(self.hero, 1)

        form_panel = QWidget()
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(32, 32, 32, 32)
        form_layout.addStretch()
        login_card = card()
        login_card.setFixedWidth(420)
        login_card.setStyleSheet("QFrame#card { background:white; border-radius:18px; border:none; }")
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(36, 34, 36, 30)
        card_layout.setSpacing(14)
        card_layout.addWidget(label("Staff sign in", "h1"))
        card_layout.addWidget(label("Enter your credentials to open the rental workspace.", "muted", wrap=True))

        # Username and password inputs
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your staff username")
        self.username_edit.setToolTip("Enter the staff username provided to you.")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)   # hide typed characters
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setToolTip("Passwords are case-sensitive")
        # "Show"/"Hide" toggle button next to the password box
        show_button = button("Show", "link", "Show or hide the password")
        show_button.setCheckable(True)
        show_button.toggled.connect(
            lambda showing: (self.password_edit.setEchoMode(QLineEdit.Normal if showing else QLineEdit.Password),
                             show_button.setText("Hide" if showing else "Show")))
        password_row = QHBoxLayout()
        password_row.addWidget(self.password_edit)
        password_row.addWidget(show_button)
        password_row.setContentsMargins(0, 0, 0, 0)
        password_container = QWidget()
        password_container.setLayout(password_row)
        self.username_field = Field("Username", self.username_edit)
        self.password_field = Field("Password", password_container)
        card_layout.addWidget(self.username_field)
        card_layout.addWidget(self.password_field)

        # General message line (wrong password, lockout countdown)
        self.message_label = label("", "error", wrap=True)
        self.message_label.hide()
        card_layout.addWidget(self.message_label)
        self.sign_in_button = button("Sign in", "primary", "Sign in (Enter)")
        self.sign_in_button.setMinimumHeight(46)
        self.sign_in_button.clicked.connect(self.attempt_login)
        card_layout.addWidget(self.sign_in_button)
        back_button = button("← Back to welcome", "link")
        back_button.clicked.connect(self.back_requested)
        card_layout.addWidget(back_button, 0, Qt.AlignHCenter)

        form_row = QHBoxLayout()
        form_row.addStretch()
        form_row.addWidget(login_card)
        form_row.addStretch()
        form_layout.addLayout(form_row)
        form_layout.addStretch()
        root_layout.addWidget(form_panel, 1)

        # Pressing Enter in either box submits the form
        self.username_edit.returnPressed.connect(self.attempt_login)
        self.password_edit.returnPressed.connect(self.attempt_login)
        # Timer that updates the lockout countdown twice a second
        self.lock_timer = QTimer(self, interval=500)
        self.lock_timer.timeout.connect(self.update_lockout)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.hero.start_photo_animation()

    def reset(self) -> None:
        """Clear the form and any errors (called each time the page is shown)."""
        self.username_edit.clear()
        self.password_edit.clear()
        self.username_field.set_error("", True)
        self.password_field.set_error("", True)
        if time.time() < self.locked_until:
            self.sign_in_button.setEnabled(False)
            if not self.lock_timer.isActive():
                self.lock_timer.start()
            self.update_lockout()
        else:
            self.message_label.hide()
        self.username_edit.setFocus()

    def update_lockout(self) -> None:
        """Show the remaining lock time, and unlock the form when it reaches zero."""
        seconds_left = ceil(self.locked_until - time.time())
        if seconds_left <= 0:
            self.lock_timer.stop()
            self.locked_until = 0.0
            self.sign_in_button.setEnabled(True)
            self.failed_attempts = 0
            self.message_label.hide()
        else:
            self.message_label.setText(f"Too many failed attempts. Try again in {seconds_left}s.")
            self.message_label.show()

    def attempt_login(self) -> None:
        """Validate the form, check the credentials and react to success or failure."""
        if time.time() < self.locked_until:
            return   # still locked out
        username, password = self.username_edit.text().strip(), self.password_edit.text()

        # 1. Both boxes must be filled in
        username_error = "" if username else "Please enter your username."
        password_error = "" if password else "Please enter your password."
        self.username_field.set_error(username_error, True)
        self.password_field.error.setText(password_error)
        self.password_field.error.setVisible(bool(password_error))
        self.password_edit.setProperty("invalid", bool(password_error))
        repolish(self.password_edit)
        self.message_label.hide()
        if username_error or password_error:
            (self.username_edit if username_error else self.password_edit).setFocus()
            return

        # 2. Compare with the fixed credentials. hmac.compare_digest takes the same time
        #    however many characters match, which avoids timing attacks.
        credentials_ok = hmac.compare_digest(username.encode(), STAFF_USERNAME.encode()) & \
            hmac.compare_digest(password.encode(), STAFF_PASSWORD.encode())
        if credentials_ok:
            self.failed_attempts = 0
            self.login_succeeded.emit()
            return

        # 3. Wrong credentials: count the failure, lock out after MAX_ATTEMPTS
        self.failed_attempts += 1
        attempts_left = self.MAX_ATTEMPTS - self.failed_attempts
        if attempts_left <= 0:
            self.locked_until = time.time() + self.LOCK_SECONDS
            self.sign_in_button.setEnabled(False)
            self.lock_timer.start()
            self.update_lockout()
        else:
            self.message_label.setText(f"Incorrect username or password. {attempts_left} attempt(s) remaining.")
            self.message_label.show()
        self.password_edit.clear()
        self.password_edit.setFocus()
