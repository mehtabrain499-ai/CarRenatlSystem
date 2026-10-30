"""
styles.py - the application-wide Qt stylesheet (QSS).

Widgets pick up their look from an objectName (e.g. a button created with
button(text, "primary") has objectName "primary" and matches QPushButton#primary).
Colours come from config.py so the theme can be changed in one place.
"""
from config import BORDER, CANVAS, DANGER, FONT, INK, LIME, MUTED

STYLE = f"""
/* Global defaults: font and text colour */
* {{ font-family: '{FONT}', 'Inter', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: {INK}; }}
QMainWindow, QStackedWidget {{ background: {CANVAS}; }}
QToolTip {{ background: {INK}; color: white; border: 1px solid #333; padding: 6px 8px; border-radius: 4px; }}
QLabel {{ background: transparent; }}
QFrame#card {{ background: white; border: 1px solid {BORDER}; border-radius: 14px; }}
QLabel#h1 {{ font-size: 26px; font-weight: 700; }}
QLabel#h2 {{ font-size: 16px; font-weight: 700; }}
QLabel#muted {{ color: {MUTED}; }}
QLabel#error {{ color: {DANGER}; font-size: 12px; }}
QLabel#req {{ color: {DANGER}; }}
QLabel#fieldlabel {{ font-weight: 600; font-size: 12px; }}

/* Text inputs and drop-downs */
QLineEdit, QComboBox {{ background: white; border: 1.5px solid #D5DAD1; border-radius: 9px;
    padding: 9px 12px; selection-background-color: {LIME}; selection-color: {INK}; }}
QLineEdit:hover, QComboBox:hover {{ border-color: #B3BAAE; }}
QLineEdit:focus, QComboBox:focus {{ border: 2px solid {INK}; padding: 8px 11px; }}
QLineEdit[invalid="true"] {{ border: 1.5px solid {DANGER}; background: #FFF6F6; }}
QLineEdit[valid="true"] {{ border: 1.5px solid #5FA316; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{ background: white; border: 1px solid {BORDER}; selection-background-color: {LIME};
    selection-color: {INK}; outline: none; }}

/* Buttons: primary (dark), lime (accent), ghost (outlined), danger, link and +/- step */
QPushButton#primary {{ background: {INK}; color: white; border: none; border-radius: 10px;
    padding: 12px 22px; font-weight: 700; }}
QPushButton#primary:hover {{ background: #2C312D; }}
QPushButton#primary:pressed {{ background: #000; }}
QPushButton#primary:disabled {{ background: #C9CEC6; color: #F4F5F2; }}
QPushButton#lime {{ background: {LIME}; color: {INK}; border: none; border-radius: 10px;
    padding: 12px 22px; font-weight: 700; }}
QPushButton#lime:hover {{ background: #CCFF7A; }}
QPushButton#lime:disabled {{ background: #3A3F3B; color: #8A918B; }}
QPushButton#ghost {{ background: transparent; color: {INK}; border: 1.5px solid #CBD1C7; border-radius: 10px;
    padding: 11px 20px; font-weight: 600; }}
QPushButton#ghost:hover {{ background: #ECEFE8; }}
QPushButton#ghostdark {{ background: transparent; color: white; border: 1.5px solid #4B514C; border-radius: 10px;
    padding: 11px 20px; font-weight: 600; }}
QPushButton#ghostdark:hover {{ background: #1E2220; }}
QPushButton#danger {{ background: transparent; color: {DANGER}; border: 1.5px solid #EBC4C6; border-radius: 10px;
    padding: 11px 20px; font-weight: 600; }}
QPushButton#danger:hover {{ background: #FDECEC; }}
QPushButton#link {{ background: transparent; border: none; color: {MUTED}; text-decoration: underline; }}
QPushButton#link:hover {{ color: {INK}; }}
QPushButton#step {{ background: #ECEFE8; border: none; border-radius: 9px; font-size: 16px; font-weight: 700;
    min-width: 38px; max-width: 38px; min-height: 38px; max-height: 38px; }}
QPushButton#step:hover {{ background: #DDE2D8; }}

/* Selectable option cards (car type, fuel, extras, licence) */
QPushButton#option {{ background: white; border: 1.5px solid #D5DAD1; border-radius: 12px; text-align: left; }}
QPushButton#option:hover {{ border-color: #8E968A; background: #FAFBF8; }}
QPushButton#option:checked {{ border: 2px solid {INK}; background: #F1FCDD; }}
QPushButton#option[invalid="true"] {{ border: 1.5px solid {DANGER}; }}
QPushButton#option:focus {{ border: 2px solid #5E6A5A; }}

/* Sidebar navigation buttons */
QPushButton#nav {{ background: transparent; color: #C9CFC7; text-align: left; border: none; border-radius: 10px;
    padding: 12px 16px; font-weight: 600; font-size: 14px; }}
QPushButton#nav:hover {{ background: #1A1E1C; color: white; }}
QPushButton#nav:checked {{ background: {LIME}; color: {INK}; }}

/* Tables and scroll bars */
QTableWidget {{ background: white; border: none; gridline-color: transparent; alternate-background-color: #FAFBF8;
    selection-background-color: #E6F9C6; selection-color: {INK}; outline: none; }}
QTableWidget::item {{ padding: 8px 10px; border-bottom: 1px solid #EEF0EB; }}
QHeaderView::section {{ background: white; color: {MUTED}; border: none; border-bottom: 1.5px solid {BORDER};
    padding: 10px; font-weight: 700; font-size: 11px; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #C5CBC0; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar:horizontal {{ height: 10px; background: transparent; }}
QScrollBar::handle:horizontal {{ background: #C5CBC0; border-radius: 4px; }}
QDialog {{ background: {CANVAS}; }}
QMessageBox {{ background: white; }}
"""
