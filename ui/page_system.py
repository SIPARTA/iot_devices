"""SYSTEM page — device & connectivity information.

Moved off the Home screen so it stays minimal. Shows the same
information the old footer provided (Internet / Camera / Sensors /
Last Update) plus basic device facts.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import platform
import sys

from ui.styles import COLORS


class _StatusRow(QWidget):
    """● Label ......... Value"""

    def __init__(self, label: str) -> None:
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self._dot = QLabel("\u25CF")
        self._dot.setFont(QFont("DejaVu Sans", 11))
        self._dot.setStyleSheet(f"color: {COLORS['status_online']};")
        lay.addWidget(self._dot)

        self._lbl = QLabel(label)
        self._lbl.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        pol = self._lbl.sizePolicy()
        from PyQt5.QtWidgets import QSizePolicy
        pol.setHorizontalPolicy(QSizePolicy.Expanding)
        self._lbl.setSizePolicy(pol)
        lay.addWidget(self._lbl)

        self._val = QLabel("\u2014")
        self._val.setFont(QFont("DejaVu Sans", 11))
        self._val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(self._val)

    def set_value(self, text: str, ok: bool) -> None:
        color = COLORS["status_online"] if ok else COLORS["status_offline"]
        self._dot.setStyleSheet(f"color: {color};")
        self._val.setText(text)
        self._val.setStyleSheet(f"color: {color};")


class SystemPage(QWidget):
    """Device / system information view."""

    logs_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(6)

        head = QHBoxLayout()
        title = QLabel("SYSTEM")
        title.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        head.addWidget(title)
        head.addStretch()

        logs_btn = QPushButton("LOGS \u203A")
        logs_btn.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        logs_btn.setFixedHeight(38)
        logs_btn.setMinimumWidth(100)
        logs_btn.clicked.connect(self.logs_requested.emit)
        head.addWidget(logs_btn)
        lay.addLayout(head)

        # ── connection status card ──────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_card']};
                border-radius: 8px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
            QWidget {{
                background: transparent;
            }}
        """)
        grid = QGridLayout(card)
        grid.setContentsMargins(14, 12, 14, 12)
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(24)

        self._inet_row = _StatusRow("INTERNET")
        self._cam_row = _StatusRow("CAMERA")
        self._sens_row = _StatusRow("SENSORS")
        grid.addWidget(self._inet_row, 0, 0)
        grid.addWidget(self._cam_row, 1, 0)
        grid.addWidget(self._sens_row, 2, 0)

        # right column — time + array info
        def _info(key: str) -> tuple[QLabel, QLabel]:
            k = QLabel(key)
            k.setFont(QFont("DejaVu Sans", 8))
            k.setStyleSheet(f"color: {COLORS['text_dim']};")
            v = QLabel("\u2014")
            v.setFont(QFont("DejaVu Sans", 12, QFont.Bold))
            v.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            box = QVBoxLayout()
            box.setContentsMargins(0, 0, 0, 0)
            box.setSpacing(0)
            box.addWidget(k)
            box.addWidget(v)
            holder = QWidget()
            holder.setLayout(box)
            return holder, v

        clock_holder, self._clock_lbl = _info("TIME")
        upd_holder, self._upd_lbl = _info("LAST UPDATE")
        arr_holder, self._array_lbl = _info("ACTIVE SENSORS")
        grid.addWidget(clock_holder, 0, 1)
        grid.addWidget(upd_holder, 1, 1)
        grid.addWidget(arr_holder, 2, 1)

        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)

        lay.addWidget(card)

        # ── device info ─────────────────────────────────────────────
        dev = QLabel(
            f"Device: Raspberry Pi \u00B7 Display 640\u00D7480   |   "
            f"Python {sys.version.split()[0]}   |   "
            f"{platform.system()}"
        )
        dev.setFont(QFont("DejaVu Sans", 9))
        dev.setWordWrap(True)
        dev.setStyleSheet(f"color: {COLORS['na_text']};")
        lay.addWidget(dev)

        note = QLabel(
            "Detail teknis sensor (ADC/Voltage) tampil di "
            "halaman SENSOR DETAIL."
        )
        note.setFont(QFont("DejaVu Sans", 9))
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {COLORS['na_text']};")
        lay.addWidget(note)

        lay.addStretch(1)

    # -- public api ------------------------------------------------------

    def update_status(
        self,
        internet: bool,
        camera: bool,
        sensors_running: bool,
    ) -> None:
        self._inet_row.set_value(
            "Connected" if internet else "Disconnected", internet
        )
        self._cam_row.set_value(
            "Connected" if camera else "Disconnected", camera
        )
        self._sens_row.set_value(
            "Running" if sensors_running else "Stopped", sensors_running
        )

    def set_clock(self, now_str: str) -> None:
        self._clock_lbl.setText(now_str)

    def set_last_update(self, when_str: str) -> None:
        self._upd_lbl.setText(when_str)

    def set_array_size(self, count: int) -> None:
        self._array_lbl.setText(f"{count} / 4")
