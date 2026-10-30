"""
WeAreCars - Car Rental Booking System
=====================================
Standalone desktop application (PySide6 / Qt) for WeAreCars, Sunderland.

Run:   pip install -r requirements.txt
       python wearecars.py

Staff login:  sta001 / givemethekeys123

Project layout (all files live in this one folder):
    wearecars.py        entry point (this file)
    config.py           business rules and theme constants
    styles.py           Qt stylesheet
    models.py           Booking data class
    pricing.py          price calculation
    validation.py       form validation rules
    storage.py          JSON saving/loading
    widgets.py          reusable UI components
    dialogs.py          booking summary dialog
    *_page.py           one file per screen (welcome, login, dashboard,
                        rented cars, booking, storage, help)
    main_window.py      main window, navigation and signal wiring
"""
import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow
from styles import STYLE


def main() -> int:
    """Create the Qt application, apply the theme, show the window and run until it is closed."""
    app = QApplication(sys.argv)
    app.setApplicationName("WeAreCars")
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
