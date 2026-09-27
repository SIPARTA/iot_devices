"""HOME page — fast monitoring view for a 640x480 display.

Layout concept:

    ┌ SENSOR ARRAY (2x2 tiles) ┐  ┌ ENVIRONMENT ┐
    │ [MiCS]      [TGS2600]    │  │     ✓       │
    │ [MQ-2]      [MQ-135]     │  │    AMAN     │
    └──────────────────────────┘  └─────────────┘

Only the essentials live here: system status is in the header,
environmental condition in the right panel, four array responses on
the left. Technical data lives on the SENSOR DETAIL page.
"""

from __future__ import annotations

from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from config.sensor_config import SENSOR_CONFIG, SENSOR_ORDER
from ui.env_panel import EnvPanel
from ui.sensor_tile import SensorTile


class HomePage(QWidget):
    """Main operator screen: array responses + environmental status."""

    def __init__(self, open_detail, parent: QWidget | None = None) -> None:
        """``open_detail``: callable(sensor_id) — invoked on tile tap."""
        super().__init__(parent)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)

        # ── left: sensor array tiles (2x2) ──────────────────────────
        self.tiles = {}
        grid = QGridLayout()
        grid.setSpacing(10)

        for idx, sid in enumerate(SENSOR_ORDER):
            cfg = SENSOR_CONFIG[sid]
            display = "TGS2600" if sid == "Figaro TGS2600" else sid
            tile = SensorTile(sid, display, cfg["min"], cfg["max"])
            tile.clicked.connect(lambda _=False, s=sid: open_detail(s))
            r, c = divmod(idx, 2)
            grid.addWidget(tile, r, c)
            self.tiles[sid] = tile

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.addLayout(grid, 1)

        lay.addLayout(left, 7)

        # ── right: environmental condition panel ────────────────────
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        self.env_panel = EnvPanel()
        right.addWidget(self.env_panel, 1)

        lay.addLayout(right, 4)
