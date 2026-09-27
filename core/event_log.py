from PyQt5.QtCore import QObject, pyqtSignal
from typing import List, Dict, Any
from datetime import datetime

INFO = "INFO"
SENSOR = "SENSOR"
SYSTEM = "SYSTEM"
WARNING = "WARNING"
ERROR = "ERROR"
GAS = "GAS"

MAX_LOG_ENTRIES = 1000

class EventLogManager(QObject):
    entry_added = pyqtSignal(dict)
    entries_cleared = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.entries: List[Dict[str, Any]] = []

    def add(self, level: str, message: str):
        entry = {
            "timestamp": datetime.now(),
            "level": level,
            "message": message
        }
        self.entries.append(entry)
        if len(self.entries) > MAX_LOG_ENTRIES:
            self.entries.pop(0)
        self.entry_added.emit(entry)

    def clear(self):
        self.entries.clear()
        self.entries_cleared.emit()

EVENT_LOG = EventLogManager()

def log_event(level: str, message: str):
    EVENT_LOG.add(level, message)
