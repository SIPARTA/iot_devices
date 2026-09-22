"""LOG page — operator-facing activity feed for SIPARTA.

640x480 notes
-------------
* compact header: ‹ BACK · LOG · [FILTER ▾] [CLEAR]
* scrollable card list; each entry = TIME + colored TYPE on one line,
  message below (wrapped, never clipped)
* newest entries at the bottom; auto-scroll only when the view is
  already at the bottom, so reading history is never interrupted
* events come exclusively from core.event_log (real app events)
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.event_log import (
    ERROR,
    EVENT_LOG,
    GAS,
    INFO,
    MAX_LOG_ENTRIES,
    SENSOR,
    SYSTEM,
    WARNING,
)
from ui.styles import COLORS

_TYPE_COLORS = {
    INFO: COLORS["text_secondary"],
    SENSOR: COLORS["accent"],
    SYSTEM: COLORS["text_primary"],
    WARNING: COLORS["status_warning"],
    ERROR: COLORS["status_danger"],
    GAS: COLORS["status_normal"],
}

_FILTER_ORDER = [None, INFO, SENSOR, SYSTEM, GAS, WARNING, ERROR]
_FILTER_LABEL = {None: "ALL", INFO: "INFO", SENSOR: "SENSOR",
                 SYSTEM: "SYSTEM", GAS: "GAS", WARNING: "WARNING",
                 ERROR: "ERROR"}


class _LogEntry(QWidget):
    """Two-line entry: `HH:MM:SS  TYPE` over the message."""

    def __init__(self, entry: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        color = _TYPE_COLORS.get(entry["type"], COLORS["text_secondary"])

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 4, 10, 5)
        lay.setSpacing(1)

        meta = QHBoxLayout()
        meta.setSpacing(8)

        time_lbl = QLabel(entry["time"])
        time_lbl.setFont(QFont("DejaVu Sans", 9))
        time_lbl.setStyleSheet(f"color: {COLORS['na_text']};")
        meta.addWidget(time_lbl)

        type_lbl = QLabel(entry["type"])
        type_lbl.setFont(QFont("DejaVu Sans", 9, QFont.Bold))
        type_lbl.setStyleSheet(f"color: {color};")
        meta.addWidget(type_lbl)
        meta.addStretch()

        lay.addLayout(meta)

        msg = QLabel(entry["message"])
        msg.setFont(QFont("DejaVu Sans", 10))
        msg.setWordWrap(True)
        pol = msg.sizePolicy()
        pol.setHorizontalPolicy(QSizePolicy.Ignored)
        msg.setSizePolicy(pol)
        msg.setStyleSheet(f"color: {COLORS['text_primary']};")
        lay.addWidget(msg)


class LogPage(QWidget):
    """Activity log view with filter and clear."""

    back_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._filter: str | None = None
        self._entry_widgets: list[tuple[dict, _LogEntry]] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 5, 8, 5)
        lay.setSpacing(3)

        # ── header ──────────────────────────────────────────────────
        head = QHBoxLayout()
        head.setSpacing(6)

        back_btn = QPushButton("\u2039 BACK")
        back_btn.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        back_btn.setFixedSize(88, 38)
        back_btn.clicked.connect(self.back_requested.emit)
        head.addWidget(back_btn)

        title = QLabel("LOG")
        title.setFont(QFont("DejaVu Sans", 13, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        head.addWidget(title)
        head.addStretch()

        self._filter_btn = QPushButton("FILTER \u25BE")
        self._filter_btn.setFont(QFont("DejaVu Sans", 10, QFont.Bold))
        self._filter_btn.setFixedHeight(36)
        self._filter_btn.setMinimumWidth(100)
        self._build_filter_menu()
        head.addWidget(self._filter_btn)

        clear_btn = QPushButton("CLEAR")
        clear_btn.setFont(QFont("DejaVu Sans", 10, QFont.Bold))
        clear_btn.setFixedHeight(36)
        clear_btn.setMinimumWidth(80)
        clear_btn.clicked.connect(self._on_clear)
        head.addWidget(clear_btn)

        lay.addLayout(head)

        # ── scrollable log card ─────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_card']};
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(0, 0, 0, 0)

        self._empty_lbl = QLabel("No system events")
        self._empty_lbl.setFont(QFont("DejaVu Sans", 12))
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._empty_lbl.setStyleSheet(f"color: {COLORS['na_text']};")
        card_lay.addWidget(self._empty_lbl)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; }}
            QWidget#logList {{ background: transparent; }}
        """)
        self._list_host = QWidget()
        self._list_host.setObjectName("logList")
        self._list_lay = QVBoxLayout(self._list_host)
        self._list_lay.setContentsMargins(0, 2, 0, 2)
        self._list_lay.setSpacing(0)
        self._list_lay.addStretch()
        self._scroll.setWidget(self._list_host)
        card_lay.addWidget(self._scroll, 1)

        lay.addWidget(card, 1)

        # live updates
        EVENT_LOG.entry_added.connect(self._on_entry_added)
        EVENT_LOG.entries_cleared.connect(self.refresh)

        self.refresh()

    # -- filter ----------------------------------------------------------

    def _build_filter_menu(self) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['btn_border']};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 18px;
                border-radius: 4px;
                color: {COLORS['text_primary']};
            }}
            QMenu::item:selected {{ background-color: #16323d; }}
        """)
        self._menu = menu
        for key in _FILTER_ORDER:
            act = menu.addAction(_FILTER_LABEL[key])
            act.setData(key if key is not None else "")
            act.triggered.connect(
                lambda _=False, k=key: self.set_filter(k)
            )

    def set_filter(self, event_type: str | None) -> None:
        label = _FILTER_LABEL.get(event_type, "ALL")
        self._filter_btn.setText(f"FILTER: {label}")
        self._filter = event_type
        self.refresh()

    # -- rendering -------------------------------------------------------

    def refresh(self) -> None:
        """Re-render the visible list from the store."""
        for _, w in self._entry_widgets:
            w.deleteLater()
        self._entry_widgets.clear()

        for entry in reversed(EVENT_LOG.filtered(self._filter)):
            self._append_widget(entry)

        self._update_empty_state()
        self._scroll_to_bottom()

    def _append_widget(self, entry: dict) -> None:
        widget = _LogEntry(entry)
        self._list_lay.insertWidget(
            self._list_lay.count() - 1, widget
        )
        self._entry_widgets.append((entry, widget))

    def _update_empty_state(self) -> None:
        empty = len(self._entry_widgets) == 0
        self._empty_lbl.setVisible(empty)
        self._scroll.setVisible(not empty)

    # -- slots -----------------------------------------------------------

    def _at_bottom(self) -> bool:
        bar = self._scroll.verticalScrollBar()
        return bar.value() >= bar.maximum() - 4

    def _scroll_to_bottom(self) -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _on_entry_added(self, entry: dict) -> None:
        if self._filter is not None and entry["type"] != self._filter:
            return
        stick = self._at_bottom()
        self._append_widget(entry)
        self._trim_oldest()
        self._update_empty_state()
        if stick:
            self._scroll_to_bottom()

    def _trim_oldest(self) -> None:
        """Keep rendered widgets in sync with the ring-buffer cap."""
        while len(self._entry_widgets) > MAX_LOG_ENTRIES:
            _, old = self._entry_widgets.pop(0)
            old.deleteLater()

    def _on_clear(self) -> None:
        # view-only clear of the in-memory GUI feed — persistent
        # storage / python logs are untouched
        EVENT_LOG.clear()
