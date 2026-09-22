"""Reusable horizontal response-bar visualisation widgets.

Used by the SENSOR ARRAY cards, the SENSOR RESPONSE PATTERN panel and
the MODEL ANALYSIS panel to show relative response levels.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.styles import COLORS


class ResponseBar(QWidget):
    """Rounded horizontal bar showing a 0..1 ratio fill."""

    def __init__(
        self,
        height: int = 12,
        track_color: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ratio: float = 0.0
        self._color: str = COLORS["bar_fill"]
        self._track: str = track_color or COLORS["bar_track"]
        self.setFixedHeight(height)
        policy = self.sizePolicy()
        policy.setHorizontalPolicy(policy.Expanding)
        self.setSizePolicy(policy)

    def set_ratio(self, ratio: float) -> None:
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()

    def set_color(self, color: str) -> None:
        self._color = color
        self.update()

    def paintEvent(self, _event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w, h = self.width(), self.height()
        r = h / 2.0

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(self._track))
        p.drawRoundedRect(0, 0, w, h, r, r)

        fw = max(h, w * self._ratio) if self._ratio > 0 else 0
        if fw > 0:
            path = QPainterPath()
            path.addRoundedRect(0.0, 0.0, fw, float(h), r, r)
            p.fillPath(path, QColor(self._color))


class BarRow(QWidget):
    """Label + ResponseBar + right-side value text in a single row."""

    def __init__(
        self,
        label: str,
        label_width: int = 92,
        bar_height: int = 10,
        value_width: int = 46,
        dim: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._lbl = QLabel(label)
        self._lbl.setFont(QFont("DejaVu Sans", 11))
        color = COLORS["text_dim"] if dim else COLORS["text_secondary"]
        self._lbl.setStyleSheet(f"color: {color};")
        self._lbl.setFixedWidth(label_width)

        self._bar = ResponseBar(bar_height)

        self._val = QLabel("—")
        self._val.setFont(QFont("DejaVu Sans", 11))
        self._val.setStyleSheet(f"color: {COLORS['na_text']};")
        self._val.setFixedWidth(value_width)
        self._val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addWidget(self._lbl)
        lay.addWidget(self._bar, 1)
        lay.addWidget(self._val)

    def update_value(
        self,
        ratio: float,
        text: str,
        color: str | None = None,
    ) -> None:
        self._bar.set_ratio(ratio)
        if color is not None:
            self._bar.set_color(color)
        self._val.setText(text)
        self._val.setStyleSheet(
            f"color: {COLORS['text_secondary'] if color is None else color};"
        )

    def set_pending(self, text: str = "—") -> None:
        """Empty / not-available state (no fabricated data)."""
        self._bar.set_ratio(0.0)
        self._bar.set_color(COLORS["bar_track"])
        self._val.setText(text)
        self._val.setStyleSheet(f"color: {COLORS['na_text']};")
