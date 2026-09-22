"""Tappable sensor tile for the Home 2x2 SENSOR ARRAY grid.

Minimal design:

    Sensor Name
    Current Value  ppm
    ● Status

plus a thin response bar so operators can see at a glance that every
array member produces its own distinct response level. Tapping the
tile opens the SENSOR DETAIL page.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from ui.response_bar import ResponseBar
from ui.styles import COLORS, STATUS_COLORS


class SensorTile(QPushButton):
    """One member of the sensor array on the Home screen."""

    def __init__(
        self,
        name: str,
        display_name: str,
        lo: float,
        hi: float,
        parent: "QPushButton | None" = None,
    ) -> None:
        super().__init__(parent)
        self._sid = name
        self._lo, self._hi = float(lo), float(hi)

        self.setMinimumSize(170, 110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(0)

        self._name = QLabel(display_name)
        self._name.setFont(QFont("DejaVu Sans", 12, QFont.Bold))
        npol = self._name.sizePolicy()
        npol.setHorizontalPolicy(QSizePolicy.Ignored)
        self._name.setSizePolicy(npol)
        lay.addWidget(self._name)

        self._value = QLabel("--")
        self._value.setFont(QFont("DejaVu Sans", 26, QFont.Bold))
        self._value.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._value, 1)

        self._unit = QLabel("ppm")
        self._unit.setFont(QFont("DejaVu Sans", 9))
        self._unit.setAlignment(Qt.AlignCenter)
        self._unit.setStyleSheet(f"color: {COLORS['text_secondary']};")
        lay.addWidget(self._unit)

        self._bar = ResponseBar(height=6)
        lay.addWidget(self._bar)

        row = QHBoxLayout()
        row.setSpacing(4)
        self._status = QLabel("NORMAL")
        self._status.setFont(QFont("DejaVu Sans", 10, QFont.Bold))
        spol = self._status.sizePolicy()
        spol.setHorizontalPolicy(QSizePolicy.Ignored)
        self._status.setSizePolicy(spol)
        row.addWidget(self._status)
        row.addStretch()
        lay.addLayout(row)

        self.update_value(float((lo + hi) / 2), "NORMAL")

    # -- update ----------------------------------------------------------

    @property
    def sensor_id(self) -> str:
        return self._sid

    def update_value(self, value: float, status: str) -> None:
        color = STATUS_COLORS.get(status, COLORS["status_error"])

        self._value.setText(f"{value:.0f}")
        span = self._hi - self._lo
        ratio = max(0.0, min(1.0, (value - self._lo) / span)) if span > 0 else 0.0
        self._bar.set_ratio(ratio)
        self._bar.set_color(color)

        self._status.setText(status)
        self._status.setStyleSheet(f"color: {color}; border: none;")

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_card']};
                border-left: 3px solid {color};
                border-radius: 8px;
            }}
            QPushButton:pressed {{
                background-color: #232734;
            }}
            QLabel {{
                border: none;
                background: transparent;
                color: #FFFFFF;
            }}
        """)
