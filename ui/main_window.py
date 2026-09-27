"""Main application window — embedded shell for a 640x480 display.

Structure:

    HEADER   SIPARTA                     ● SYSTEM ONLINE
    ────────────────────────────────────────────────────────
    STACK    HOME | GAS ANALYSIS | MATRIX | DETAIL | SYSTEM
    ────────────────────────────────────────────────────────
    NAV      [HOME] [GAS] [SENSORS] [SYSTEM]   (touch targets)

Data flow is unchanged: SensorManager -> widgets every tick;
EnvironmentalStatusManager drives the ENVIRONMENT panel.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Ensure root is in sys.path so we can resolve blockchain_services and ai_models
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.sensor_config import (
    CLOCK_UPDATE_MS,
    SENSOR_CONFIG,
    SENSOR_ORDER,
    SENSOR_UPDATE_MS,
    STATUS_UPDATE_MS,
)
from core.detection import DetectionPipeline
from core.environmental_status import EnvironmentalStatusManager
from core.event_log import ERROR, INFO, SENSOR, SYSTEM, WARNING, log_event
from core import hardware_output as hw
from core.sensor_manager import SensorManager
from core.system_status import SystemStatusProvider
from ui.home_page import HomePage
from ui.navbar import NavBar
from ui.page_detail import DetailPage
from ui.page_gas import GasPage
from ui.page_log import LogPage
from ui.page_matrix import MatrixPage
from ui.page_system import SystemPage
from ui.styles import COLORS

logger = logging.getLogger(__name__)

PAGE_HOME = 0
PAGE_GAS = 1
PAGE_MATRIX = 2
PAGE_DETAIL = 3
PAGE_SYSTEM = 4
PAGE_LOG = 5

# which nav button stays lit while a sub-page is open
_NAV_ALIAS = {
    PAGE_HOME: PAGE_HOME,
    PAGE_GAS: PAGE_GAS,
    PAGE_MATRIX: PAGE_GAS,
    PAGE_DETAIL: PAGE_DETAIL,
    PAGE_SYSTEM: PAGE_SYSTEM,
    PAGE_LOG: PAGE_SYSTEM,
}


class MainWindow(QMainWindow):
    """640x480 industrial monitoring dashboard."""

    def __init__(self) -> None:
        super().__init__()

        self._sensor_mgr = SensorManager()
        self._sys_status = SystemStatusProvider()
        self._env_mgr = EnvironmentalStatusManager()

        self._init_window()
        self._init_header()
        self._init_pages()
        self._init_navbar()

        # blockchain detection pipeline (background thread; optional)
        self._detections = DetectionPipeline(self._sensor_mgr)

        self._init_timers()

        logger.info("Dashboard ready")

    def set_calibrating(self, value: bool) -> None:
        """Forward calibration state to the sensor manager."""
        self._sensor_mgr.set_calibrating(value)

    # ── window ----------------------------------------------------------

    def _init_window(self) -> None:
        self.setWindowTitle("SIPARTA")
        self.setFixedSize(640, 480)
        self.setStyleSheet(f"background-color: {COLORS['bg_main']};")

        self._root = QWidget()
        self.setCentralWidget(self._root)
        self._vbox = QVBoxLayout(self._root)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)

    # ── header ----------------------------------------------------------

    def _init_header(self) -> None:
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['header_bg']};
                border-bottom: 1px solid {COLORS['border_card']};
            }}
        """)

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(8)

        title = QLabel("SIPARTA")
        title.setFont(QFont("DejaVu Sans", 15, QFont.Bold))
        title.setStyleSheet(
            f"color: {COLORS['text_primary']}; border: none;"
            f"background: transparent;"
        )
        lay.addWidget(title)
        lay.addStretch()

        self._sys_lbl = QLabel("\u25CF SYSTEM ONLINE")
        self._sys_lbl.setFont(QFont("DejaVu Sans", 10, QFont.Bold))
        self._sys_lbl.setStyleSheet(
            f"color: {COLORS['status_online']}; border: none;"
            f"background: transparent;"
        )
        lay.addWidget(self._sys_lbl)

        self._vbox.addWidget(bar)

    # ── pages -----------------------------------------------------------

    def _init_pages(self) -> None:
        self.stack = QStackedWidget()

        self._home = HomePage(open_detail=self.open_sensor_detail)
        self._gas = GasPage()
        self._matrix = MatrixPage()
        self._detail = DetailPage()
        self._system = SystemPage()
        self._log = LogPage()

        for page in (
            self._home,
            self._gas,
            self._matrix,
            self._detail,
            self._system,
            self._log,
        ):
            self.stack.addWidget(page)

        self._vbox.addWidget(self.stack, 1)

        # gas analysis has no model yet → explicit waiting state
        self._gas.set_all_pending()
        self._system.set_array_size(len(SENSOR_ORDER))

        # sub-page navigation
        self._gas.back_requested.connect(lambda: self.show_page(PAGE_HOME))
        self._gas.matrix_requested.connect(lambda: self.show_page(PAGE_MATRIX))
        self._matrix.back_requested.connect(lambda: self.show_page(PAGE_GAS))
        self._detail.back_requested.connect(lambda: self.show_page(PAGE_HOME))
        self._system.logs_requested.connect(
            lambda: self.show_page(PAGE_LOG)
        )
        self._log.back_requested.connect(
            lambda: self.show_page(PAGE_SYSTEM)
        )

        # real startup events → operator log
        log_event(SYSTEM, "System started")
        log_event(SENSOR, f"{len(SENSOR_ORDER)} sensors initialised")
        log_event(INFO, "Gas analysis unavailable")

        # transition trackers for the tick hooks
        self._prev_sensor_statuses: dict[str, str | None] = {
            sid: None for sid in SENSOR_ORDER
        }
        self._prev_env_level: int | None = None
        self._prev_conn: tuple[bool, bool, bool] | None = None

    def show_page(self, page_idx: int) -> None:
        self.stack.setCurrentIndex(page_idx)
        if self._nav is not None:
            self._nav.set_active(_NAV_ALIAS.get(page_idx, PAGE_HOME))

    def open_sensor_detail(self, sid: str) -> None:
        self._detail.set_sensor(sid)
        self.show_page(PAGE_DETAIL)

    # ── navbar ----------------------------------------------------------

    def _init_navbar(self) -> None:
        self._nav: NavBar | None = None
        nav = NavBar(items=[
            (PAGE_HOME, "HOME"),
            (PAGE_GAS, "GAS"),
            (PAGE_DETAIL, "SENSORS"),
            (PAGE_SYSTEM, "SYSTEM"),
        ])
        nav.active_changed.connect(self.show_page)
        nav.set_active(PAGE_HOME)
        self._nav = nav
        self._vbox.addWidget(nav)

    # ── timers ----------------------------------------------------------

    def _init_timers(self) -> None:
        self._t_sensor = QTimer(self)
        self._t_sensor.timeout.connect(self._tick_sensors)
        self._t_sensor.start(SENSOR_UPDATE_MS)

        self._t_clock = QTimer(self)
        self._t_clock.timeout.connect(self._tick_clock)
        self._t_clock.start(CLOCK_UPDATE_MS)

        self._t_status = QTimer(self)
        self._t_status.timeout.connect(self._tick_status)
        self._t_status.start(STATUS_UPDATE_MS)

        self._tick_sensors()
        self._tick_clock()
        self._tick_status()

    # ── ticks -----------------------------------------------------------

    def _tick_sensors(self) -> None:
        self._sensor_mgr.update_all()

        statuses: dict[str, str] = {}
        for sid in SENSOR_ORDER:
            value = self._sensor_mgr.get_value(sid)
            status = self._sensor_mgr.get_status(sid)
            statuses[sid] = status
            self._home.tiles[sid].update_value(value, status)

            prev = self._prev_sensor_statuses[sid]
            if prev is not None and prev != status:
                if status == "WARNING":
                    log_event(WARNING, f"{sid}: {prev} \u2192 {status}")
                elif status in ("DANGER", "ERROR"):
                    log_event(ERROR, f"{sid}: {prev} \u2192 {status}")
                else:
                    log_event(SENSOR, f"{sid}: {prev} \u2192 {status}")
            self._prev_sensor_statuses[sid] = status

        self._detail.update_value(
            self._sensor_mgr.get_value(self._detail.sensor_id),
            self._sensor_mgr.get_status(self._detail.sensor_id),
        )

        self._gas.update_gas_values(self._sensor_mgr)

        env_result = self._env_mgr.calculate(statuses)
        self._home.env_panel.update_status(env_result)
        level = env_result["status"]
        if self._prev_env_level is not None and level != self._prev_env_level:
            label = env_result["label"]
            etype = (
                INFO if level == 0
                else WARNING if level == 1
                else ERROR
            )
            log_event(etype, f"Environment: {label}")
        self._prev_env_level = level
        hw.set_level(level)

        if level >= 1:
            hw.start_alarm()
        else:
            hw.stop_alarm()

        # detection snapshot → local store → blockchain (async, optional)
        self._detections.on_environment_update(env_result)

        self._last_update_str = datetime.now().strftime("%H:%M:%S")
        self._system.set_last_update(self._last_update_str)

    def _tick_clock(self) -> None:
        self._system.set_clock(datetime.now().strftime("%H:%M:%S"))

    def _tick_status(self) -> None:
        self._sys_status.refresh()
        self._sys_status.set_sensors_running(
            self._sensor_mgr.are_sensors_running()
        )
        inet = self._sys_status.get_internet_status()
        cam = self._sys_status.get_camera_status()
        sens = self._sys_status.get_sensors_running()
        self._system.update_status(inet, cam, sens)

        conn = (inet, cam, sens)
        if self._prev_conn is not None and conn != self._prev_conn:
            names = ("Internet", "Camera", "Sensors")
            for i, name in enumerate(names):
                if conn[i] != self._prev_conn[i]:
                    state = "connected" if conn[i] else "disconnected"
                    if name == "Sensors":
                        state = "running" if conn[i] else "stopped"
                    log_event(SYSTEM, f"{name} {state}")
        self._prev_conn = conn

        if inet:
            self._sys_lbl.setText("\u25CF SYSTEM ONLINE")
            self._sys_lbl.setStyleSheet(
                f"color: {COLORS['status_online']}; border: none;"
                f"background: transparent;"
            )
        else:
            self._sys_lbl.setText("\u25CF SYSTEM OFFLINE")
            self._sys_lbl.setStyleSheet(
                f"color: {COLORS['status_offline']}; border: none;"
                f"background: transparent;"
            )

    # ── keyboard --------------------------------------------------------

    def keyPressEvent(self, event) -> None:  # noqa: N802
        key = event.key()
        if key == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
        elif key == Qt.Key_F11:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()
        else:
            super().keyPressEvent(event)
