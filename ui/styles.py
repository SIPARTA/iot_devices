"""Theme colours and application-wide stylesheet — tuned for a
640x480 display on Raspberry Pi (embedded industrial look).
"""

COLORS = {
    "bg_main": "#0f1117",
    "bg_card": "#1a1d27",
    "border_card": "#2a2d37",
    "header_bg": "#141720",
    "text_primary": "#FFFFFF",
    "text_secondary": "#b0b0b0",
    "text_dim": "#5f6368",
    "accent": "#00bcd4",
    "gauge_bg": "#2a2d37",
    "gauge_value_green": "#00c853",
    "gauge_value_orange": "#ff9100",
    "gauge_value_red": "#ff1744",
    "status_normal": "#00c853",
    "status_warning": "#ff9100",
    "status_danger": "#ff1744",
    "env_safe": "#00D26A",
    "env_warning": "#FFC107",
    "env_danger": "#FF3B30",
    "status_error": "#b71c1c",
    "status_online": "#00e676",
    "status_offline": "#ff5252",
    # touch / compact additions
    "bar_track": "#232633",
    "bar_fill": "#00bcd4",
    "na_text": "#5f6368",
    "section_title": "#8a919e",
    "table_row_alt": "#1e212c",
    "btn_bg": "#1e212c",
    "btn_border": "#343947",
}

STATUS_COLORS = {
    "NORMAL": COLORS["status_normal"],
    "WARNING": COLORS["status_warning"],
    "DANGER": COLORS["status_danger"],
    "ERROR": COLORS["status_error"],
}

APP_STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_main']};
}}
QWidget {{
    color: {COLORS['text_primary']};
}}
QLabel {{
    border: none;
    background: transparent;
}}

/* ── generic touch button ─────────────────────────────────────── */
QPushButton {{
    background-color: {COLORS['btn_bg']};
    border: 1px solid {COLORS['btn_border']};
    border-radius: 8px;
    padding: 4px 10px;
    font-weight: bold;
}}
QPushButton:pressed {{
    background-color: #2a2e3c;
}}

/* ── bottom navigation bar buttons ────────────────────────────── */
QStackedWidget {{
    border: none;
}}
"""

NAV_BTN_QSS = f"""
QPushButton {{
    background-color: {COLORS['header_bg']};
    color: {COLORS['text_secondary']};
    border: none;
    border-top: 2px solid transparent;
    border-radius: 0;
    padding: 0;
}}
QPushButton:checked {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['accent']};
    border-top: 2px solid {COLORS['accent']};
}}
QPushButton:pressed {{
    background-color: {COLORS['bg_card']};
}}
"""
