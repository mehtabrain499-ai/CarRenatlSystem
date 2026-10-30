"""
intro_page.py - the animated opening screen.

Three cars drive in from the right-hand side of the window and park in the
centre, with their wheels spinning and speed lines streaming behind them. Once
they have stopped, the WeAreCars name fades in underneath. The screen then hands
over to the welcome page. Click or press any key to skip it.

Everything is painted by hand in paintEvent(); a single QVariantAnimation
("timeline") counts from 0.0 to 1.0 and each part of the scene works out how far
through its own slice of that timeline it is.
"""
from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QWidget

from config import FONT, INK, LIME, SIDEBAR
from widgets import draw_car

TOTAL_MS = 5600                                   # length of the whole intro in milliseconds
CAR_COLOURS = ("#3D7BFF", "#E5383B", "#F5F7FF")   # left, centre and right car
START_DELAYS = (0.00, 0.14, 0.28)                 # when each car starts (fraction of the timeline)
DRIVE_SPAN = 0.36                                 # how long each car takes to arrive (fraction of the timeline)


def clamp01(value: float) -> float:
    """Limit a number to the range 0.0 - 1.0."""
    return max(0.0, min(1.0, value))


def segment(timeline: float, start: float, end: float) -> float:
    """How far (0.0 - 1.0) the timeline is through the slice that runs from `start` to `end`."""
    return clamp01((timeline - start) / (end - start))


def ease_out_cubic(progress: float) -> float:
    """Easing curve: starts fast and slows down gently, like a car braking to a stop."""
    return 1.0 - (1.0 - progress) ** 3


def draw_speed_streaks(painter: QPainter, tail_x: float, car_top: float, car_height: float, speed: float) -> None:
    """Draw faint horizontal lines trailing behind a moving car. `speed` is 0.0 (stopped) to 1.0 (full speed)."""
    painter.save()
    for height_ratio, length in ((0.45, 140), (0.58, 100), (0.70, 170)):
        y = car_top + car_height * height_ratio
        painter.setPen(QPen(QColor(255, 255, 255, int(120 * speed)), 2, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(QPointF(tail_x + 10, y), QPointF(tail_x + 10 + length * speed, y))
    painter.restore()


class IntroPage(QWidget):
    """Full-window animation shown when the program starts."""

    finished = Signal()   # emitted when the animation ends or the user skips it

    def __init__(self) -> None:
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)     # needed so key presses reach keyPressEvent
        self.setCursor(Qt.PointingHandCursor)
        self.progress = 0.0                     # current position on the timeline, 0.0 - 1.0
        self.is_done = False
        self.timeline = QVariantAnimation(self)
        self.timeline.setStartValue(0.0)
        self.timeline.setEndValue(1.0)
        self.timeline.setDuration(TOTAL_MS)
        self.timeline.setEasingCurve(QEasingCurve.Linear)
        self.timeline.valueChanged.connect(self.on_tick)
        self.timeline.finished.connect(self.finish)

    def start(self) -> None:
        """Begin (or restart) the animation."""
        self.is_done = False
        self.progress = 0.0
        self.setFocus()
        self.timeline.start()

    def on_tick(self, value) -> None:
        """Called on every animation frame: remember the new position and redraw."""
        self.progress = float(value)
        self.update()

    def finish(self) -> None:
        """End the intro (only once) and tell the main window to show the welcome page."""
        if self.is_done:
            return
        self.is_done = True
        self.timeline.stop()
        self.finished.emit()

    def mousePressEvent(self, _event) -> None:
        """Clicking anywhere skips the animation."""
        self.finish()

    def keyPressEvent(self, _event) -> None:
        """Pressing any key skips the animation."""
        self.finish()

    def paintEvent(self, _event) -> None:
        """Draw the whole scene for the current point on the timeline."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()
        timeline = self.progress

        # ---- Background: dark navy gradient with faint rings ----
        background = QLinearGradient(0, 0, 0, height)
        background.setColorAt(0, QColor(SIDEBAR))
        background.setColorAt(1, QColor(INK))
        painter.fillRect(self.rect(), background)
        painter.setPen(QPen(QColor(189, 252, 90, 28), 2))
        for ring in range(5):
            painter.drawEllipse(QPointF(width / 2, height * 0.40), 160 + ring * 110, 160 + ring * 110)

        # ---- Layout measurements (everything scales with the window) ----
        car_width = min(width * 0.22, 330.0)
        car_height = car_width * 0.46
        car_top = height * 0.26
        road_top = car_top + car_height * 0.89
        road_height = car_height * 0.36

        # ---- Road with a dashed centre line that scrolls while the cars are driving ----
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(8, 11, 30))
        painter.drawRect(QRectF(0, road_top, width, road_height))
        painter.setPen(QPen(QColor(189, 252, 90, 110), 2))
        painter.drawLine(QPointF(0, road_top), QPointF(width, road_top))
        driving = segment(timeline, 0.0, START_DELAYS[-1] + DRIVE_SPAN)
        dash_scroll = ease_out_cubic(driving) * 900          # total distance the dashes travel left
        dash_y = road_top + road_height * 0.55
        painter.setPen(QPen(QColor(255, 255, 255, 60), 3, Qt.SolidLine, Qt.RoundCap))
        for index in range(-2, int(width / 80) + 3):
            dash_x = index * 80 - (dash_scroll % 80)
            painter.drawLine(QPointF(dash_x, dash_y), QPointF(dash_x + 40, dash_y))

        # ---- The three cars ----
        spacing = car_width * 1.25
        final_centres = (width / 2 - spacing, width / 2, width / 2 + spacing)
        start_centre = width + car_width                      # completely off-screen on the right
        wheel_radius = car_height * 0.17
        for colour, delay, final_x in zip(CAR_COLOURS, START_DELAYS, final_centres):
            drive = segment(timeline, delay, delay + DRIVE_SPAN)
            centre_x = start_centre + (final_x - start_centre) * ease_out_cubic(drive)
            if 0.0 < drive < 1.0:
                # Speed lines fade out as the car slows down
                draw_speed_streaks(painter, centre_x + car_width / 2, car_top, car_height, (1.0 - drive) ** 2)
            car_rect = QRectF(centre_x - car_width / 2, car_top, car_width, car_height)
            distance_driven = start_centre - centre_x
            draw_car(painter, car_rect, QColor(colour), facing_left=True, wheel_angle=distance_driven / wheel_radius)

        # ---- "WE ARE CARS" name fades in and rises beneath the road ----
        title_progress = ease_out_cubic(segment(timeline, 0.60, 0.78))
        tagline_progress = ease_out_cubic(segment(timeline, 0.74, 0.90))
        title_top = road_top + road_height + height * 0.09
        if title_progress > 0:
            painter.save()
            painter.setOpacity(title_progress)
            title_font = QFont(FONT, max(24, int(width * 0.04)), QFont.Weight.Bold)
            title_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 8)
            metrics = QFontMetricsF(title_font)
            pieces = (("WE", "#FFFFFF"), ("ARE", LIME), ("CARS", "#FFFFFF"))
            piece_widths = [metrics.horizontalAdvance(text) for text, _colour in pieces]
            cursor_x = width / 2 - sum(piece_widths) / 2
            baseline_y = title_top + (1.0 - title_progress) * 26 + metrics.ascent()   # slides up as it fades in
            painter.setFont(title_font)
            for (text, colour), piece_width in zip(pieces, piece_widths):
                painter.setPen(QColor(colour))
                painter.drawText(QPointF(cursor_x, baseline_y), text)
                cursor_x += piece_width
            painter.restore()

        if tagline_progress > 0:
            painter.save()
            painter.setOpacity(tagline_progress)
            # Short accent underline that grows outwards from the centre
            underline_half = 60 * tagline_progress
            painter.setPen(QPen(QColor(LIME), 3, Qt.SolidLine, Qt.RoundCap))
            underline_y = title_top + max(24, int(width * 0.04)) * 2.1
            painter.drawLine(QPointF(width / 2 - underline_half, underline_y), QPointF(width / 2 + underline_half, underline_y))
            tagline_font = QFont(FONT, 12, QFont.Weight.DemiBold)
            tagline_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 6)
            painter.setFont(tagline_font)
            painter.setPen(QColor("#B4BAD6"))
            painter.drawText(QRectF(0, underline_y + 14, width, 30), Qt.AlignHCenter | Qt.AlignTop,
                             "SUNDERLAND · CAR RENTAL")
            painter.restore()

        # ---- Small "skip" hint at the bottom ----
        painter.setOpacity(0.55 * segment(timeline, 0.05, 0.20))
        painter.setFont(QFont(FONT, 10))
        painter.setPen(QColor("#B4BAD6"))
        painter.drawText(QRectF(0, height - 46, width, 24), Qt.AlignHCenter | Qt.AlignVCenter,
                         "Click or press any key to skip")
        painter.end()