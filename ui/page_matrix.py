"""SENSOR MATRIX page — Sensor x Gas Detection Matrix (reference).

Kept as an information/reference view of the array's response
capabilities. Deliberately NOT part of the Home screen: on a 640x480
display the Home stays minimal.
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

from config.sensor_config import (
    SENSOR_CONFIG,
    SENSOR_GAS_MATRIX,
    SENSOR_ORDER,
)
from ui.styles import COLORS

_CHECK = "\u2713"
_DOT = "\u00B7"


def _short_name(sid: str) -> str:
    if sid == "Figaro TGS2600":
        return "TGS2600"
    return sid


class MatrixPage(QWidget):
    """Compact reference table: which array members respond to which gas."""

    back_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(6)

        # sub-header
        head = QHBoxLayout()
        head.setSpacing(8)

        back_btn = QPushButton("\u2039 BACK")
        back_btn.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        back_btn.setFixedSize(94, 36)
        back_btn.clicked.connect(self.back_requested.emit)
        head.addWidget(back_btn)

        title = QLabel("SENSOR \u00D7 GAS MATRIX")
        title.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        head.addWidget(title)
        head.addStretch()
        lay.addLayout(head)

        caption = QLabel(
            "Referensi capability \u2014 deteksi aktual dari pola gabungan "
            "sensor array, bukan pengukuran spesifik per sensor."
        )
        caption.setFont(QFont("DejaVu Sans", 9))
        caption.setWordWrap(True)
        caption.setStyleSheet(f"color: {COLORS['text_secondary']};")
        lay.addWidget(caption)

        # matrix card
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
        """)
        grid = QGridLayout(card)
        grid.setContentsMargins(10, 8, 10, 8)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(2)

        hdr_font = QFont("DejaVu Sans", 9, QFont.Bold)

        corner = QLabel("GAS")
        corner.setFont(hdr_font)
        corner.setStyleSheet(f"color: {COLORS['section_title']};")
        grid.addWidget(corner, 0, 0)

        for c, sid in enumerate(SENSOR_ORDER, start=1):
            hdr = QLabel(_short_name(sid))
            hdr.setFont(hdr_font)
            hdr.setAlignment(Qt.AlignCenter)
            hdr.setStyleSheet(f"color: {COLORS['accent']};")
            grid.addWidget(hdr, 0, c)
        grid.setRowMinimumHeight(0, 26)

        row_font = QFont("DejaVu Sans", 10, QFont.Bold)
        cell_font = QFont("DejaVu Sans", 12)

        for r_idx, (gas, responders) in enumerate(SENSOR_GAS_MATRIX.items(), start=1):
            gas_lbl = QLabel(gas)
            gas_lbl.setFont(row_font)
            gas_lbl.setStyleSheet("color: #FFFFFF;")
            grid.addWidget(gas_lbl, r_idx, 0)

            for c, sid in enumerate(SENSOR_ORDER, start=1):
                if sid in responders:
                    cell = QLabel(_CHECK)
                    cell.setFont(cell_font)
                    cell.setAlignment(Qt.AlignCenter)
                    cell.setStyleSheet("color: #00e676;")
                else:
                    cell = QLabel(_DOT)
                    cell.setFont(cell_font)
                    cell.setAlignment(Qt.AlignCenter)
                    cell.setStyleSheet(f"color: {COLORS['na_text']};")
                grid.addWidget(cell, r_idx, c)

            grid.setRowMinimumHeight(r_idx, 26)

        legend = QLabel(
            f"{_CHECK} merespons parameter ini   {_DOT} bukan target utama"
        )
        legend.setFont(QFont("DejaVu Sans", 9))
        legend.setStyleSheet(f"color: {COLORS['text_secondary']};")
        grid.addWidget(
            legend, len(SENSOR_GAS_MATRIX) + 1, 0, 1, len(SENSOR_ORDER) + 1
        )

        grid.setColumnStretch(0, 3)
        for c in range(1, len(SENSOR_ORDER) + 1):
            grid.setColumnStretch(c, 2)

        lay.addWidget(card, 1)
