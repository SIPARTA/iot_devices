import socket
from PyQt5.QtCore import QObject, pyqtSignal

class SystemStatusProvider(QObject):
    status_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._internet_status = False
        self._camera_status = False
        self._sensors_running = True

    def refresh(self):
        self._internet_status = self._check_internet()
        # Mock camera status check
        self._camera_status = True
        self.status_updated.emit()

    def _check_internet(self, host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False

    def get_internet_status(self) -> bool:
        return self._internet_status

    def get_camera_status(self) -> bool:
        return self._camera_status

    def get_sensors_running(self) -> bool:
        return self._sensors_running

    def set_sensors_running(self, running: bool):
        self._sensors_running = running
        self.status_updated.emit()
