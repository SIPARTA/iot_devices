"""GAS ANALYSIS page — multi-sensor pattern analysis results.

Each gas value is the average ppm from all sensors that detect it
(defined in SENSOR_GAS_MATRIX). Status uses the minimum warning/danger
threshold across contributing sensors.

Optimised for a 640x480 display:
* compact title / subtitle
* gas list paginated 4 rows per page (GAS 1/2 · GAS 2/2) with large
  PREVIOUS / NEXT buttons — guarantees generous row heights so no
  value or status text is ever clipped or overlapped
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.sensor_config import GAS_ORDER, SENSOR_CONFIG, SENSOR_GAS_MATRIX, SENSOR_ORDER
from ui.styles import COLORS, STATUS_COLORS

_NA_VALUE = "\u2014"
_NA_STATUS = "N/A"
_NA_COLOR = COLORS["na_text"]

_ROWS_PER_PAGE = 4


class _GasRow(QWidget):
    """One gas parameter line: NAME | VALUE | STATUS."""

    def __init__(self, gas: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._gas = gas
        self.setFixedHeight(38)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(10)

        self.name_lbl = QLabel(gas)
        self.name_lbl.setFont(QFont("DejaVu Sans", 12, QFont.Bold))
        self.name_lbl.setStyleSheet("color: #FFFFFF;")
        pol = self.name_lbl.sizePolicy()
        pol.setHorizontalPolicy(QSizePolicy.Expanding)
        self.name_lbl.setSizePolicy(pol)
        lay.addWidget(self.name_lbl, 2)

        self.value_lbl = QLabel(_NA_VALUE)
        self.value_lbl.setFont(QFont("DejaVu Sans", 14, QFont.Bold))
        self.value_lbl.setAlignment(Qt.AlignCenter)
        pol = self.value_lbl.sizePolicy()
        pol.setHorizontalPolicy(QSizePolicy.Expanding)
        self.value_lbl.setSizePolicy(pol)
        lay.addWidget(self.value_lbl, 2)

        self.status_lbl = QLabel(_NA_STATUS)
        self.status_lbl.setFont(QFont("DejaVu Sans", 11))
        self.status_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pol = self.status_lbl.sizePolicy()
        pol.setHorizontalPolicy(QSizePolicy.Expanding)
        self.status_lbl.setSizePolicy(pol)
        lay.addWidget(self.status_lbl, 2)

        self.set_pending()

    # -- state -----------------------------------------------------------

    @property
    def gas(self) -> str:
        return self._gas

    def set_state(
        self,
        value_text: str,
        status_text: str,
        color: str | None = None,
    ) -> None:
        self.value_lbl.setText(value_text)
        self.value_lbl.setStyleSheet(f"color: {color or COLORS['text_primary']};")
        self.status_lbl.setText(status_text)
        self.status_lbl.setStyleSheet(
            f"color: {color or COLORS['status_normal']};"
        )

    def set_pending(self) -> None:
        self.value_lbl.setText(_NA_VALUE)
        self.value_lbl.setStyleSheet(f"color: {_NA_COLOR};")
        self.status_lbl.setText(_NA_STATUS)
        self.status_lbl.setStyleSheet(f"color: {_NA_COLOR};")


class _GasTablePage(QFrame):
    """One paginated table card holding up to four rows."""

    def __init__(self, gases: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"""
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

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 6, 0, 6)
        lay.setSpacing(2)

        lay.addWidget(self._header_block())

        # gas rows
        self.rows: dict[str, _GasRow] = {}
        for gas in gases:
            row = _GasRow(gas)
            self.rows[gas] = row
            lay.addWidget(row)

    def _header_block(self) -> QWidget:
        """Header — shares the exact column geometry as the data rows."""
        head = QWidget()
        head.setStyleSheet("background: transparent;")
        h = QHBoxLayout(head)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(10)

        for text, align in (
            ("GAS", Qt.AlignLeft | Qt.AlignVCenter),
            ("VALUE", Qt.AlignHCenter | Qt.AlignVCenter),
            ("STATUS", Qt.AlignRight | Qt.AlignVCenter),
        ):
            lbl = QLabel(text)
            lbl.setFont(QFont("DejaVu Sans", 9, QFont.Bold))
            lbl.setAlignment(align)
            lbl.setStyleSheet(f"color: {COLORS['section_title']};")
            proc = lbl.sizePolicy()
            proc.setHorizontalPolicy(QSizePolicy.Expanding)
            lbl.setSizePolicy(proc)
            h.addWidget(lbl, 1)
        return head

    def all_rows(self) -> dict[str, _GasRow]:
        return self.rows


class GasPage(QWidget):
    """GAS ANALYSIS page with pagination and matrix access."""

    back_requested = pyqtSignal()
    matrix_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._pages: list[list[str]] = [
            GAS_ORDER[i:i + _ROWS_PER_PAGE]
            for i in range(0, len(GAS_ORDER), _ROWS_PER_PAGE)
        ]
        self._page_idx: int = 0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(6)

        # ── sub-header ──────────────────────────────────────────────
        head = QHBoxLayout()
        head.setSpacing(10)

        head_col = QVBoxLayout()
        head_col.setSpacing(0)
        title = QLabel("GAS ANALYSIS")
        title.setFont(QFont("DejaVu Sans", 13, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        head_col.addWidget(title)

        sub = QLabel("Multi-Sensor Pattern Analysis")
        sub.setFont(QFont("DejaVu Sans", 9))
        spol = sub.sizePolicy()
        spol.setHorizontalPolicy(QSizePolicy.Ignored)
        sub.setSizePolicy(spol)
        sub.setStyleSheet(f"color: {COLORS['text_secondary']};")
        head_col.addWidget(sub)

        head.addLayout(head_col, 1)
        head.addStretch()

        matrix_btn = QPushButton("MATRIX \u203A")
        matrix_btn.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        matrix_btn.setFixedHeight(38)
        matrix_btn.setMinimumWidth(100)
        matrix_btn.clicked.connect(self.matrix_requested.emit)
        head.addWidget(matrix_btn)

        lay.addLayout(head)

        # ── paginated gas tables ────────────────────────────────────
        self.stack = QStackedWidget()
        self.table_pages: list[_GasTablePage] = []
        for chunk in self._pages:
            page = _GasTablePage(chunk)
            self.table_pages.append(page)
            self.stack.addWidget(page)
        lay.addWidget(self.stack, 1)

        # ── pager row ───────────────────────────────────────────────
        pager = QHBoxLayout()
        pager.setSpacing(10)

        self.prev_btn = QPushButton("\u2039 PREV")
        self.prev_btn.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        self.prev_btn.setMinimumHeight(38)
        self.prev_btn.clicked.connect(self._go_prev)
        pager.addWidget(self.prev_btn, 1)

        self.indicator = QLabel("GAS 1/2")
        self.indicator.setFont(QFont("DejaVu Sans", 10, QFont.Bold))
        self.indicator.setAlignment(Qt.AlignCenter)
        self.indicator.setStyleSheet(f"color: {COLORS['section_title']};")
        pager.addWidget(self.indicator, 0)

        self.next_btn = QPushButton("NEXT \u203A")
        self.next_btn.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        self.next_btn.setMinimumHeight(38)
        self.next_btn.clicked.connect(self._go_next)
        pager.addWidget(self.next_btn, 1)

        lay.addLayout(pager)

        self._update_pager()

    # -- pagination ------------------------------------------------------

    def _go_prev(self) -> None:
        if self._page_idx > 0:
            self._page_idx -= 1
            self._update_pager()

    def _go_next(self) -> None:
        if self._page_idx < len(self._pages) - 1:
            self._page_idx += 1
            self._update_pager()

    def _update_pager(self) -> None:
        self.stack.setCurrentIndex(self._page_idx)
        total = len(self._pages)
        self.indicator.setText(f"GAS {self._page_idx + 1}/{total}")
        self.prev_btn.setEnabled(self._page_idx > 0)
        self.next_btn.setEnabled(self._page_idx < total - 1)
        for btn in (self.prev_btn, self.next_btn):
            btn.setStyleSheet(
                f"QPushButton {{ color: {COLORS['text_primary'] if btn.isEnabled() else COLORS['na_text']}; }}"
            )

    # -- data update ------------------------------------------------------

    def update_gas_values(self, sensor_mgr) -> None:
        """Compute average ppm per gas from contributing sensors."""
        for gas in GAS_ORDER:
            sids = SENSOR_GAS_MATRIX.get(gas, [])
            if not sids:
                self.set_gas_state(gas, "—", "N/A", COLORS["na_text"])
                continue

            ppm_values = [sensor_mgr.get_value(sid) for sid in sids]
            avg_ppm = sum(ppm_values) / len(ppm_values)

            # minimum threshold across contributing sensors
            w_warn = min(SENSOR_CONFIG[s]["warning_threshold"] for s in sids)
            w_danger = min(SENSOR_CONFIG[s]["danger_threshold"] for s in sids)

            if avg_ppm >= w_danger:
                status, color = "DANGER", STATUS_COLORS["DANGER"]
            elif avg_ppm >= w_warn:
                status, color = "WARNING", STATUS_COLORS["WARNING"]
            else:
                status, color = "NORMAL", STATUS_COLORS["NORMAL"]

            self.set_gas_state(gas, f"{avg_ppm:.0f}", status, color)

    def set_gas_state(
        self,
        gas: str,
        value_text: str,
        status_text: str,
        color: str | None = None,
    ) -> None:
        for page in self.table_pages:
            row = page.all_rows().get(gas)
            if row is not None:
                row.set_state(value_text, status_text, color)
                return

    def set_all_pending(self) -> None:
        for page in self.table_pages:
            for row in page.all_rows().values():
                row.set_pending()
