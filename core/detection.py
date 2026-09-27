import time
import json
import os
import uuid
import logging
from core.event_log import log_event, SENSOR, GAS
from blockchain_services.service import BlockchainService

logger = logging.getLogger("siparta.detection")

class DetectionPipeline:
    def __init__(self, sensor_manager):
        self.sensor_mgr = sensor_manager
        self.blockchain = BlockchainService.instance()
        self.last_report_time = 0.0
        self.cooldown_s = 60.0
        self.data_dir = "data/detections"
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def on_environment_update(self, env_result: dict):
        status = env_result.get("status", "NORMAL")
        if status in ["BAHAYA", "WASPADA"]:
            now = time.time()
            if now - self.last_report_time >= self.cooldown_s:
                self.last_report_time = now
                self._trigger_detection(status)

    def _trigger_detection(self, status: str):
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "classification": status,
            "mics5524": self.sensor_mgr.get_value("mics5524"),
            "tgs2600": self.sensor_mgr.get_value("tgs2600"),
            "mq2": self.sensor_mgr.get_value("mq2"),
            "mq135": self.sensor_mgr.get_value("mq135"),
            "image_url": "", # Mock for now
            "blockchain_status": "pending"
        }
        
        # Save local snapshot
        file_path = os.path.join(self.data_dir, f"det_{record['timestamp']}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(record, f, indent=2)
            log_event(SENSOR, f"Local snapshot saved: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save local snapshot: {e}")
            
        # Trigger blockchain
        if self.blockchain.enabled:
            log_event(GAS, f"{status} detected! Sending to blockchain...")
            self.blockchain.submit(record, self._on_blockchain_result)
            
    def _on_blockchain_result(self, record: dict, result: dict):
        if result.get("status") == "success":
            msg = f"Blockchain success: tx {result.get('transaction_hash')}"
            log_event(SENSOR, msg)
        else:
            msg = f"Blockchain failed: {result.get('error')}"
            log_event(SENSOR, msg)
