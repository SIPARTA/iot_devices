from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt

class DetailPage(QWidget):
    back_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sensor_id = ""
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel("Sensor Detail")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.value_label = QLabel("Value: -- V")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        self.status_label = QLabel("Status: --")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.back_button = QPushButton("Kembali")
        self.back_button.clicked.connect(self.back_requested.emit)
        layout.addWidget(self.back_button)

    def set_sensor(self, sensor_id: str):
        self.sensor_id = sensor_id
        self.title_label.setText(f"Sensor: {sensor_id.upper()}")

    def update_value(self, value: float, status: str):
        self.value_label.setText(f"Value: {value:.2f} V")
        self.status_label.setText(f"Status: {status}")
