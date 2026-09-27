"""Full-screen warmup overlay shown on first launch.

Displays a 60-second countdown while gas sensors heat up.
Blocks all interaction with the main window until complete.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from core import hardware_output as hw
from ui.styles import COLORS

WARMUP_SECONDS = 60


class WarmupSplash(QWidget):
    """Modal-style full-screen overlay with countdown."""

    finished = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._remaining = WARMUP_SECONDS
        self._init_ui()
        self._init_timer()

    # ── layout ─────────────────────────────────────────────────────

    def _init_ui(self) -> None:
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(self.backgroundRole(), QColor(COLORS['bg_main']))
        self.setPalette(pal)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(10)
        lay.setContentsMargins(40, 40, 40, 40)

        # ── top text block ────────────────────────────────────────
        title = QLabel("KALIBRASI SENSOR")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(30)
        title.setFont(QFont("DejaVu Sans", 18, QFont.Bold))
        title.setStyleSheet(
            f"color: {COLORS['accent']}; background: transparent;"
        )
        lay.addWidget(title)

        sub = QLabel("Pemanasan sensor gas — mohon tunggu")
        sub.setAlignment(Qt.AlignCenter)
        sub.setFont(QFont("DejaVu Sans", 10))
        sub.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent;"
        )
        lay.addWidget(sub)

        lay.addSpacing(24)

        # ── countdown block ───────────────────────────────────────
        self._countdown_lbl = QLabel(self._fmt(self._remaining))
        self._countdown_lbl.setAlignment(Qt.AlignCenter)
        self._countdown_lbl.setFixedHeight(56)
        self._countdown_lbl.setFont(QFont("DejaVu Sans", 42, QFont.Bold))
        self._countdown_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent;"
        )
        # lay.addWidget(self._countdown_lbl)

        lay.addSpacing(24)

        # ── progress block (bar + label in their own container) ──
        prog_box = QWidget()
        prog_box.setStyleSheet("background: transparent;")
        prog_lay = QVBoxLayout(prog_box)
        prog_lay.setContentsMargins(0, 0, 0, 0)
        prog_lay.setSpacing(10)
        prog_lay.setAlignment(Qt.AlignCenter)

        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedWidth(360)
        self._bar.setFixedHeight(16)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bar_track']};
                border: 1px solid {COLORS['border_card']};
                border-radius: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['accent']};
                border-radius: 7px;
            }}
        """)
        prog_lay.addWidget(self._bar, alignment=Qt.AlignCenter)

        self._progress_lbl = QLabel("0% · Pemanasan sensor gas")
        self._progress_lbl.setAlignment(Qt.AlignCenter)
        self._progress_lbl.setFixedHeight(20)
        self._progress_lbl.setFont(QFont("DejaVu Sans", 11))
        self._progress_lbl.setStyleSheet(
            f"color: {COLORS['text_secondary']}; background: transparent;"
        )
        # prog_lay.addWidget(self._progress_lbl, alignment=Qt.AlignCenter)

        lay.addWidget(prog_box, alignment=Qt.AlignCenter)

    # ── timer ──────────────────────────────────────────────────────

    def _init_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self) -> None:
        self._remaining -= 1
        if self._remaining <= 0:
            self._timer.stop()
            # self._countdown_lbl.setText("SELESAI")
            self._bar.setValue(100)
            # self._progress_lbl.setText("100% · Sensor siap digunakan")
            hw.beep(2)
            QTimer.singleShot(500, self.finished.emit)
            return

        # self._countdown_lbl.setText(self._fmt(self._remaining))
        pct = int((WARMUP_SECONDS - self._remaining) / WARMUP_SECONDS * 100)
        self._bar.setValue(pct)
        # self._progress_lbl.setText(f"{pct}% · Pemanasan sensor gas")

    # ── helpers ────────────────────────────────────────────────────

    @staticmethod
    def _fmt(seconds: int) -> str:
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"

    # ── sizing ─────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().geometry())
