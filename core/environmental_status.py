import sys
import os
from pathlib import Path

# Ensure root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_models.inference import run_inference

class EnvironmentalStatusManager:
    @staticmethod
    def calculate(statuses: dict, sensor_values: list = None) -> dict:
        """
        Calculate the aggregate environment status based on all sensors.
        Returns a dict:
        {
            "status": "AMAN" | "WASPADA" | "BAHAYA",
            "message": "deskripsi singkat"
        }
        """
        if any(s == "CALIBRATING" for s in statuses.values()):
            return {"status": "CALIBRATING", "message": "Sensor sedang kalibrasi..."}
            
        # If we have precise sensor readings, run AI inference
        if sensor_values and len(sensor_values) == 4:
            status = run_inference(sensor_values)
            message = "Kondisi udara normal."
            if status == "BAHAYA":
                message = "Gas berbahaya terdeteksi oleh AI!"
            elif status == "WASPADA":
                message = "Level gas tidak normal (WASPADA)."
            return {"status": status, "message": message}
            
        # Fallback to simple threshold if no values provided
        danger_count = sum(1 for s in statuses.values() if s == "DANGER")
        warning_count = sum(1 for s in statuses.values() if s == "WARNING")
        
        if danger_count > 0:
            return {"status": "BAHAYA", "message": f"{danger_count} gas berbahaya terdeteksi!"}
        elif warning_count > 0:
            return {"status": "WASPADA", "message": f"{warning_count} gas dalam level waspada."}
        else:
            return {"status": "AMAN", "message": "Kondisi udara normal."}
