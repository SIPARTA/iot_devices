import logging
import random
from config.sensor_config import SENSOR_CONFIG, SENSOR_ORDER

logger = logging.getLogger("siparta.sensor_manager")

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    IS_RPI = True
except ImportError:
    IS_RPI = False


class SensorManager:
    """Manages reading from the ADS1115 ADC and updating sensor statuses."""
    
    def __init__(self):
        self.running = True
        self.calibrating = False
        self.values = {sid: 0.0 for sid in SENSOR_ORDER}
        self.statuses = {sid: "NORMAL" for sid in SENSOR_ORDER}
        
        self.ads = None
        self.channels = {}
        
        global IS_RPI
        if IS_RPI:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.ads = ADS.ADS1115(i2c)
                self.channels = {
                    "mics5524": AnalogIn(self.ads, ADS.P0),
                    "tgs2600": AnalogIn(self.ads, ADS.P1),
                    "mq2": AnalogIn(self.ads, ADS.P2),
                    "mq135": AnalogIn(self.ads, ADS.P3)
                }
                logger.info("ADS1115 initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize ADC: {e}")
                IS_RPI = False

    def update_all(self):
        if not self.running:
            return
            
        for sid in SENSOR_ORDER:
            if IS_RPI and sid in self.channels:
                try:
                    voltage = self.channels[sid].voltage
                except Exception as e:
                    logger.error(f"Error reading {sid}: {e}")
                    voltage = random.uniform(1.0, 3.5)
            else:
                voltage = random.uniform(1.0, 3.5)
                
            self.values[sid] = voltage
            
            config = SENSOR_CONFIG.get(sid, {})
            warning_threshold = config.get("warning", 2.0)
            danger_threshold = config.get("danger", 3.0)
            
            if voltage >= danger_threshold:
                self.statuses[sid] = "DANGER"
            elif voltage >= warning_threshold:
                self.statuses[sid] = "WARNING"
            else:
                self.statuses[sid] = "NORMAL"

    def get_value(self, sensor_id):
        return self.values.get(sensor_id, 0.0)

    def get_status(self, sensor_id):
        if self.calibrating:
            return "CALIBRATING"
        return self.statuses.get(sensor_id, "NORMAL")

    def set_calibrating(self, is_calibrating: bool):
        self.calibrating = is_calibrating

    def are_sensors_running(self):
        return self.running
