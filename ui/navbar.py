"""Bottom navigation bar — large touch targets for a resistive
touchscreen (640x480 display).

Buttons are checkable; exactly one is checked at a time and maps to
a page index in the main QStackedWidget.
"""

from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ui.styles import NAV_BTN_QSS


class NavBar(QWidget):
    """Persistent bottom navigation with finger-sized buttons."""

    active_changed = pyqtSignal(int)

    def __init__(self, items: list[tuple[int, str]], parent: QWidget | None = None) -> None:
        """``items``: list of ``(page_index, label)``."""
        super().__init__(parent)
        self._btns: dict[int, QPushButton] = {}
        self.setFixedHeight(64)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(1)

        for page_idx, label in items:
            btn = QPushButton(label)
            btn.setFont(QFont("DejaVu Sans", 13, QFont.Bold))
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_BTN_QSS)
            btn.clicked.connect(lambda _checked=False, p=page_idx: self.active_changed.emit(p))
            lay.addWidget(btn, 1)
            self._btns[page_idx] = btn

    # -- behaviour -------------------------------------------------------

    def set_active(self, page_idx: int) -> None:
        """Highlight ``page_idx`` without emitting (programmatic nav)."""
        for idx, btn in self._btns.items():
            btn.setChecked(idx == page_idx)

    def button_for(self, page_idx: int) -> QPushButton | None:
        return self._btns.get(page_idx)
