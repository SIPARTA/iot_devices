"""Compact ENVIRONMENT panel for the 640x480 Home page.

Shows the overall condition (AMAN / WASPADA / BAHAYA) using the
existing EnvironmentalStatusManager result dict. No new status logic
is introduced.

Long-press (3 s) on the panel reveals a system admin popup with
close / restart / shutdown actions.
"""

from __future__ import annotations

import logging
import subprocess

from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.styles import COLORS

logger = logging.getLogger(__name__)

_LONG_PRESS_MS = 3000


class StatusIcon(QWidget):
    """Small painted icon that reflects the current severity level."""

    _FILL = {0: "#00D26A", 1: "#FFC107", 2: "#FF3B30"}

    def __init__(self, size: int = 60, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._level: int = 0
        self.setFixedSize(size, size)

    def setLevel(self, level: int) -> None:  # noqa: N802
        self._level = level
        self.update()

    def paintEvent(self, _event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        r = min(w, h) / 2.0 - 2.0
        fill = QColor(self._FILL.get(self._level, self._FILL[0]))

        p.setPen(Qt.NoPen)
        p.setBrush(fill)

        if self._level == 0:
            # AMAN : circle + checkmark
            p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
            p.setPen(QPen(QColor("white"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            path = QPainterPath()
            path.moveTo(cx - r * 0.30, cy + r * 0.02)
            path.lineTo(cx - r * 0.05, cy + r * 0.32)
            path.lineTo(cx + r * 0.35, cy - r * 0.25)
            p.drawPath(path)

        elif self._level == 1:
            # WASPADA : triangle + !
            tri = QPolygonF([
                QPointF(cx, cy - r),
                QPointF(cx - r * 0.90, cy + r * 0.72),
                QPointF(cx + r * 0.90, cy + r * 0.72),
            ])
            p.drawPolygon(tri)
            p.setPen(QColor("white"))
            p.setBrush(Qt.NoBrush)
            p.setFont(QFont("DejaVu Sans", max(10, int(r * 0.8)), QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, "!")

        else:
            # BAHAYA : diamond + !
            dia = QPolygonF([
                QPointF(cx, cy - r),
                QPointF(cx + r * 0.72, cy),
                QPointF(cx, cy + r),
                QPointF(cx - r * 0.72, cy),
            ])
            p.drawPolygon(dia)
            p.setPen(QColor("white"))
            p.setBrush(Qt.NoBrush)
            p.setFont(QFont("DejaVu Sans", max(10, int(r * 0.8)), QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, "!")


class AdminDialog(QDialog):
    """Popup with system admin actions (close / restart / shutdown)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("System Admin")
        self.setFixedSize(220, 160)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_main']};
                border: 2px solid {COLORS['accent']};
                border-radius: 10px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(8)

        title = QLabel("SYSTEM ADMIN")
        title.setFont(QFont("DejaVu Sans", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['accent']};")
        lay.addWidget(title)

        btn_style = f"""
            QPushButton {{
                background-color: {COLORS['btn_bg']};
                border: 1px solid {COLORS['btn_border']};
                border-radius: 6px;
                color: {COLORS['text_primary']};
                padding: 6px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #2a2e3c;
            }}
        """

        btn_close = QPushButton("Close App")
        btn_close.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet(btn_style)
        btn_close.clicked.connect(self._close_app)
        lay.addWidget(btn_close)

        btn_restart = QPushButton("Restart")
        btn_restart.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        btn_restart.setFixedHeight(36)
        btn_restart.setStyleSheet(btn_style)
        btn_restart.clicked.connect(self._restart)
        lay.addWidget(btn_restart)

        btn_shutdown = QPushButton("Shutdown")
        btn_shutdown.setFont(QFont("DejaVu Sans", 11, QFont.Bold))
        btn_shutdown.setFixedHeight(36)
        btn_shutdown.setStyleSheet(btn_style)
        btn_shutdown.clicked.connect(self._shutdown)
        lay.addWidget(btn_shutdown)

    # -- handlers --------------------------------------------------------

    def _close_app(self) -> None:
        logger.info("Admin: closing application")
        QApplication.quit()

    def _restart(self) -> None:
        logger.info("Admin: restarting system")
        self.close()
        subprocess.Popen(["sudo", "shutdown", "-r", "now"])

    def _shutdown(self) -> None:
        logger.info("Admin: shutting down system")
        self.close()
        subprocess.Popen(["sudo", "shutdown", "-h", "now"])


class EnvPanel(QFrame):
    """Compact environmental condition card for the Home screen."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._press_timer = QTimer(self)
        self._press_timer.setSingleShot(True)
        self._press_timer.setInterval(_LONG_PRESS_MS)
        self._press_timer.timeout.connect(self._show_admin)
        self._build()

    def _build(self) -> None:
        self.setFixedWidth(190)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_card']};
                border-radius: 10px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(6)
        lay.addStretch(2)

        self._icon = StatusIcon(64)
        lay.addWidget(self._icon, alignment=Qt.AlignCenter)

        self._status_lbl = QLabel("AMAN")
        self._status_lbl.setFont(QFont("DejaVu Sans", 20, QFont.Bold))
        self._status_lbl.setAlignment(Qt.AlignCenter)
        self._status_lbl.setStyleSheet(f"color: {COLORS['env_safe']};")
        lay.addWidget(self._status_lbl)

        lay.addStretch(3)

    def update_status(self, result: dict) -> None:
        level = result["status"]
        color = result["color"]

        self._icon.setLevel(level)

        self._status_lbl.setText(result["label"])
        self._status_lbl.setStyleSheet(
            f"border: none; background: transparent; color: {color};"
        )

    # -- long-press admin popup ------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._press_timer.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._press_timer.stop()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        self._press_timer.stop()
        super().mouseMoveEvent(event)

    def _show_admin(self) -> None:
        dlg = AdminDialog(self)
        dlg.exec_()
