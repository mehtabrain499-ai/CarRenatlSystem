"""
widgets.py - reusable UI building blocks used by several pages.

Contains small helper functions (label, button, card), custom-painted widgets
(Hero, BarChart), the selectable option cards, the labelled form Field with
inline error messages, the days input with +/- buttons, and table helpers.
"""
from __future__ import annotations

from math import cos, pi, sin

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import (QAbstractItemView, QButtonGroup, QFrame, QGridLayout, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from config import DAILY_RATE, FONT, INK, LIME, MAX_DAYS, MIN_DAYS, MUTED, SIDEBAR


# --------------------------------------------------------------------------------------
# Small helper functions
# --------------------------------------------------------------------------------------
def label(text: str, name: str = "", wrap: bool = False) -> QLabel:
    """Create a QLabel. `name` becomes its objectName so the stylesheet can style it."""
    text_label = QLabel(text)
    if name:
        text_label.setObjectName(name)
    text_label.setWordWrap(wrap)
    return text_label


def button(text: str, kind: str = "primary", tip: str = "") -> QPushButton:
    """Create a styled button. `kind` selects the style (primary, lime, ghost, danger...)."""
    push_button = QPushButton(text)
    push_button.setObjectName(kind)
    push_button.setCursor(Qt.PointingHandCursor)
    if tip:
        push_button.setToolTip(tip)
    return push_button


def card() -> QFrame:
    """Create a white rounded panel (styled by QFrame#card in the stylesheet)."""
    frame = QFrame()
    frame.setObjectName("card")
    return frame


def repolish(widget: QWidget) -> None:
    """Force Qt to re-apply the stylesheet after a dynamic property (e.g. invalid) changed."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def scroll_wrap(content: QWidget) -> QScrollArea:
    """Wrap a page in a scroll area so it stays usable in a small window."""
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.NoFrame)
    scroll_area.setWidget(content)
    return scroll_area


def page_header(title: str, subtitle: str) -> QVBoxLayout:
    """Standard page heading: a large title with a muted line beneath it."""
    layout = QVBoxLayout()
    layout.setSpacing(2)
    layout.addWidget(label(title, "h1"))
    layout.addWidget(label(subtitle, "muted"))
    return layout


# --------------------------------------------------------------------------------------
# Splash artwork
# --------------------------------------------------------------------------------------
def draw_car(
    painter: QPainter,
    rect: QRectF,
    color: QColor,
    *,
    facing_left: bool = False,
    wheel_angle: float = 0.0,
) -> None:
    """Draw a vector side-view car inside `rect`.

    All coordinates are fractions (0.0 - 1.0) of the rectangle, so the car
    scales to any window size. `facing_left` mirrors the car and `wheel_angle`
    rotates the wheel spokes in radians.
    """
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing)
    if facing_left:
        painter.translate(rect.left() + rect.right(), 0)
        painter.scale(-1, 1)
    left, top, width, height = rect.x(), rect.y(), rect.width(), rect.height()

    def point_at(x_ratio: float, y_ratio: float) -> QPointF:
        """Convert a fractional position inside the rectangle to real pixel coordinates."""
        return QPointF(left + x_ratio * width, top + y_ratio * height)

    # Soft shadow under the car
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(0, 0, 0, 90))
    painter.drawEllipse(QRectF(left + width * 0.05, top + height * 0.84, width * 0.9, height * 0.12))

    # Car body outline
    body = QPainterPath(point_at(0.02, 0.72))
    for x_ratio, y_ratio in [(0.03, 0.55), (0.20, 0.49), (0.31, 0.27), (0.45, 0.16), (0.68, 0.16),
                             (0.80, 0.38), (0.96, 0.47), (0.985, 0.72)]:
        body.lineTo(point_at(x_ratio, y_ratio))
    body.closeSubpath()
    gradient = QLinearGradient(point_at(0, 0.15), point_at(0, 0.75))
    gradient.setColorAt(0, color.lighter(125))
    gradient.setColorAt(1, color.darker(130))
    painter.setBrush(gradient)
    painter.setPen(QPen(color.darker(130), 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawPath(body)

    # Front and rear windows
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(20, 28, 34, 230))
    painter.drawPolygon(QPolygonF([point_at(0.33, 0.30), point_at(0.46, 0.21), point_at(0.545, 0.21),
                                   point_at(0.545, 0.47), point_at(0.27, 0.47)]))
    painter.drawPolygon(QPolygonF([point_at(0.575, 0.21), point_at(0.67, 0.21), point_at(0.765, 0.41),
                                   point_at(0.575, 0.47)]))

    # Headlight
    painter.setBrush(QColor(LIME))
    painter.drawRoundedRect(QRectF(left + width * 0.955, top + height * 0.52, width * 0.035, height * 0.06), 3, 3)

    # Two wheels: tyre, rim, then hub
    for wheel_x in (0.24, 0.77):
        wheel_center = point_at(wheel_x, 0.74)
        wheel_radius = height * 0.17
        painter.setBrush(QColor(12, 14, 13))
        painter.drawEllipse(wheel_center, wheel_radius, wheel_radius)
        painter.setBrush(QColor(170, 176, 170))
        painter.drawEllipse(wheel_center, wheel_radius * 0.55, wheel_radius * 0.55)
        painter.setPen(QPen(QColor(90, 96, 90), max(1, width * 0.006)))
        for spoke in range(3):
            angle = wheel_angle + spoke * pi / 3
            spoke_end = QPointF(
                wheel_center.x() + cos(angle) * wheel_radius * 0.45,
                wheel_center.y() + sin(angle) * wheel_radius * 0.45,
            )
            painter.drawLine(wheel_center, spoke_end)
        painter.setBrush(QColor(60, 64, 60))
        painter.drawEllipse(wheel_center, wheel_radius * 0.2, wheel_radius * 0.2)
    painter.restore()


class Hero(QWidget):
    """Display a bundled real-car photo with an optional cinematic zoom."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        image_path = Path(__file__).resolve().parent / "assets" / "car-hero.jpg"
        self.car_photo = QPixmap(str(image_path))
        if self.car_photo.isNull():
            raise RuntimeError(f"Could not load the car photo: {image_path}")
        self.photo_zoom = 1.0
        self.photo_animation = QVariantAnimation(self)
        self.photo_animation.setDuration(1800)
        self.photo_animation.setStartValue(0.0)
        self.photo_animation.setEndValue(1.0)
        self.photo_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.photo_animation.valueChanged.connect(self.set_photo_animation_progress)

    def start_photo_animation(self) -> None:
        """Slowly zoom toward the car whenever the login panel is shown."""
        self.photo_zoom = 1.0
        self.photo_animation.start()

    def set_photo_animation_progress(self, progress: object) -> None:
        self.photo_zoom = 1.0 + 0.12 * float(progress)
        self.update()

    def paintEvent(self, _event) -> None:
        """Scale the photo to fill the panel while keeping the car in view."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        target = QRectF(self.rect())
        source_aspect = self.car_photo.width() / self.car_photo.height()
        target_aspect = target.width() / target.height()
        if source_aspect > target_aspect:
            source_width = self.car_photo.height() * target_aspect
            source_left = (self.car_photo.width() - source_width) * 0.76
            source = QRectF(source_left, 0, source_width, self.car_photo.height())
        else:
            source_height = self.car_photo.width() / target_aspect
            source_top = (self.car_photo.height() - source_height) / 2
            source = QRectF(0, source_top, self.car_photo.width(), source_height)
        focus_x, focus_y = 0.64, 0.55
        source = QRectF(
            source.x() + source.width() * focus_x * (1 - 1 / self.photo_zoom),
            source.y() + source.height() * focus_y * (1 - 1 / self.photo_zoom),
            source.width() / self.photo_zoom,
            source.height() / self.photo_zoom,
        )
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(target, self.car_photo, source)

        overlay = QLinearGradient(0, 0, self.width(), 0)
        overlay.setColorAt(0, QColor(13, 16, 15, 75))
        overlay.setColorAt(1, QColor(13, 16, 15, 5))
        painter.fillRect(self.rect(), overlay)
        painter.end()


class WelcomeArtwork(QWidget):
    """Paint a continuously animated illustrated car for the welcome screen."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.progress = 0.0
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(2400)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(2 * pi)
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self.set_progress)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.animation.start()

    def hideEvent(self, event) -> None:
        self.animation.stop()
        super().hideEvent(event)

    def set_progress(self, value: object) -> None:
        self.progress = float(value)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()

        background = QLinearGradient(0, 0, 0, height)
        background.setColorAt(0, QColor(SIDEBAR))
        background.setColorAt(1, QColor(INK))
        painter.fillRect(self.rect(), background)

        ring_radius = min(width, height) * 0.19
        painter.setPen(QPen(QColor(189, 252, 90, 32), 2))
        for ring in range(1, 5):
            radius = ring_radius * ring
            painter.drawEllipse(QPointF(width / 2, height * 0.48), radius, radius)

        car_width = min(width * 0.74, 460.0)
        car_height = car_width * 0.46
        bob = sin(self.progress) * min(height * 0.008, 6.0)
        car_top = (height - car_height) / 2 + bob
        travel = width * 0.10
        centre_x = width / 2 + sin(self.progress) * travel
        car_rect = QRectF(centre_x - car_width / 2, car_top, car_width, car_height)
        draw_car(
            painter,
            car_rect,
            QColor("#E5383B"),
            facing_left=cos(self.progress) < 0,
            wheel_angle=self.progress * 3,
        )
        painter.end()


# --------------------------------------------------------------------------------------
# Selectable options
# --------------------------------------------------------------------------------------
class OptionCard(QPushButton):
    """A large checkable button showing a title and a smaller subtitle (e.g. the price)."""

    def __init__(self, title: str, subtitle: str, tip: str) -> None:
        super().__init__()
        self.setObjectName("option")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tip)
        self.setMinimumHeight(62)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(1)
        title_label = label(title)
        title_label.setStyleSheet("font-weight:700; font-size:14px;")
        subtitle_label = label(subtitle)
        subtitle_label.setStyleSheet(f"color:{MUTED}; font-size:12px;")
        for text_label in (title_label, subtitle_label):
            # Let clicks pass through the labels so the whole card acts as the button.
            text_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(text_label)


class OptionGroup(QWidget):
    """A grid of OptionCards. Single choice (radio style) or multi choice (toggle style)."""

    selection_changed = Signal()  # emitted whenever any card is checked or unchecked

    def __init__(self, options: list[tuple[str, str, str]], columns: int = 2, multi: bool = False) -> None:
        """`options` is a list of (title, subtitle, tooltip) tuples."""
        super().__init__()
        self.multi = multi
        self.cards: dict[str, OptionCard] = {}
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(not multi)   # exclusive = only one card can be checked
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        for index, (title, subtitle, tip) in enumerate(options):
            option_card = OptionCard(title, subtitle, tip)
            option_card.toggled.connect(lambda _checked=False: self.selection_changed.emit())
            self.button_group.addButton(option_card)
            self.cards[title] = option_card
            grid.addWidget(option_card, index // columns, index % columns)

    def value(self) -> str | None:
        """Title of the selected card, or None if nothing is selected."""
        return next((title for title, option_card in self.cards.items() if option_card.isChecked()), None)

    def checked(self, title: str) -> bool:
        """True if the card with this title is currently selected."""
        return self.cards[title].isChecked()

    def set_invalid(self, invalid: bool) -> None:
        """Show or hide the red 'invalid' border on every card."""
        for option_card in self.cards.values():
            option_card.setProperty("invalid", invalid)
            repolish(option_card)

    def reset(self) -> None:
        """Deselect every card (exclusive mode must be switched off briefly to allow this)."""
        self.button_group.setExclusive(False)
        for option_card in self.cards.values():
            option_card.setChecked(False)
        self.button_group.setExclusive(not self.multi)


# --------------------------------------------------------------------------------------
# Form field
# --------------------------------------------------------------------------------------
class Field(QWidget):
    """Label + input widget + inline error message (+ optional hint and ? tooltip)."""

    def __init__(self, text: str, widget: QWidget, required: bool = True, hint: str = "", tip: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        # Top row: field label, red * if mandatory, and a "?" help icon with a tooltip
        label_row = QHBoxLayout()
        label_row.setSpacing(2)
        label_row.addWidget(label(text, "fieldlabel"))
        if required:
            required_star = label("*", "req")
            required_star.setToolTip("Mandatory field")
            label_row.addWidget(required_star)
        if tip:
            help_icon = label("  ?")
            help_icon.setToolTip(tip)
            help_icon.setCursor(Qt.WhatsThisCursor)
            help_icon.setStyleSheet(f"color:{MUTED}; font-weight:700;")
            label_row.addWidget(help_icon)
        label_row.addStretch()
        layout.addLayout(label_row)
        layout.addWidget(widget)
        # Optional grey hint shown under the input until an error replaces it
        self.hint = label(hint, "muted") if hint else None
        if self.hint:
            self.hint.setStyleSheet("font-size:11px;")
            layout.addWidget(self.hint)
        # Red error message, hidden until set_error() is called with some text
        self.error = label("", "error", wrap=True)
        self.error.hide()
        layout.addWidget(self.error)
        self.widget = widget
        if tip:
            widget.setToolTip(tip)

    def set_error(self, message: str, ok_when_empty: bool = False) -> None:
        """Show `message` (or clear it if empty) and colour the input red/green.

        ok_when_empty=True means "don't paint the green 'valid' border" - used
        when resetting a form so untouched fields stay neutral.
        """
        self.error.setText(message)
        self.error.setVisible(bool(message))
        if self.hint:
            self.hint.setVisible(not message)
        # Some inputs (DaysInput) wrap a QLineEdit in `.edit`; style that inner widget.
        target = getattr(self.widget, "edit", self.widget)
        if isinstance(target, OptionGroup):
            target.set_invalid(bool(message))
        else:
            target.setProperty("invalid", bool(message))
            target.setProperty("valid", (not message) and not ok_when_empty)
            repolish(target)


class DaysInput(QWidget):
    """Number-of-days input: a text box with - and + buttons and a price note."""

    # These two signal names deliberately copy QLineEdit's names so DaysInput can be
    # wired up in exactly the same way as a normal text field.
    textChanged = Signal(str)
    editingFinished = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        minus_button = button("−", "step", "One day fewer")
        plus_button = button("+", "step", "One day more")
        self.edit = QLineEdit("1")
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setMaxLength(3)
        self.edit.setMaximumWidth(90)
        self.edit.textChanged.connect(self.textChanged)
        self.edit.editingFinished.connect(self.editingFinished)
        minus_button.clicked.connect(lambda: self.nudge(-1))
        plus_button.clicked.connect(lambda: self.nudge(1))
        for part in (minus_button, self.edit, plus_button):
            layout.addWidget(part)
        layout.addWidget(label(f"day(s)   ·   £{DAILY_RATE} per day", "muted"))
        layout.addStretch()

    def nudge(self, step: int) -> None:
        """Add or subtract days, keeping the value within MIN_DAYS..MAX_DAYS."""
        try:
            current_days = int(self.edit.text())
        except ValueError:
            current_days = MIN_DAYS   # box was empty or invalid - start again from the minimum
        self.edit.setText(str(min(MAX_DAYS, max(MIN_DAYS, current_days + step))))
        self.editingFinished.emit()

    def text(self) -> str:
        """Current text in the box (same name as QLineEdit.text())."""
        return self.edit.text()


# --------------------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------------------
class SortItem(QTableWidgetItem):
    """Table cell that sorts by a hidden value (e.g. a number or date) instead of its text."""

    def __lt__(self, other: QTableWidgetItem) -> bool:
        my_key, other_key = self.data(Qt.UserRole), other.data(Qt.UserRole)
        if my_key is not None and other_key is not None:
            return my_key < other_key
        return super().__lt__(other)


def make_table(headers: list[str]) -> QTableWidget:
    """Create a read-only, row-selectable table with the given column headings."""
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels([header.upper() for header in headers])
    table.verticalHeader().hide()
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)      # cells cannot be edited
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setShowGrid(False)
    table.setFocusPolicy(Qt.StrongFocus)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.verticalHeader().setDefaultSectionSize(44)
    return table


def set_row(table: QTableWidget, row: int, cells: list[tuple[str, object]],
            right_aligned_columns: tuple[int, ...] = ()) -> None:
    """Fill one table row. Each cell is (text to show, value to sort by)."""
    for column, (text, sort_key) in enumerate(cells):
        item = SortItem(text)
        item.setData(Qt.UserRole, sort_key)
        if column in right_aligned_columns:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)   # numbers read better right-aligned
        table.setItem(row, column, item)


# --------------------------------------------------------------------------------------
# Chart
# --------------------------------------------------------------------------------------
class BarChart(QWidget):
    """Horizontal bar chart: bookings per vehicle type (painted by hand, no chart library)."""

    def __init__(self) -> None:
        super().__init__()
        self.data: list[tuple[str, int]] = []   # (vehicle name, number of bookings)
        self.setMinimumHeight(190)

    def set_data(self, data: list[tuple[str, int]]) -> None:
        """Replace the chart data and redraw."""
        self.data = data
        self.update()

    def paintEvent(self, _event) -> None:
        """Draw one row per vehicle: name, grey track, lime bar, count."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        largest_value = max([value for _name, value in self.data] + [1])   # +[1] avoids dividing by zero
        row_height = self.height() / max(len(self.data), 1)
        painter.setFont(QFont(FONT, 10))
        for index, (name, value) in enumerate(self.data):
            row_top = index * row_height
            # Vehicle name on the left
            painter.setPen(QColor(INK))
            painter.drawText(QRectF(0, row_top, 100, row_height), Qt.AlignVCenter | Qt.AlignLeft, name)
            # Grey background track
            track = QRectF(110, row_top + row_height * 0.30, self.width() - 160, row_height * 0.40)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#ECEFE8"))
            painter.drawRoundedRect(track, 6, 6)
            # Lime bar, scaled against the largest value (minimum width 12 so small values stay visible)
            if value:
                painter.setBrush(QColor(LIME))
                bar_width = max(12, track.width() * value / largest_value)
                painter.drawRoundedRect(QRectF(track.x(), track.y(), bar_width, track.height()), 6, 6)
            # Count on the right
            painter.setPen(QColor(INK))
            painter.drawText(QRectF(self.width() - 40, row_top, 40, row_height),
                             Qt.AlignVCenter | Qt.AlignRight, str(value))
        painter.end()
