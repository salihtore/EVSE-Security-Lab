import time
import json
import threading
import logging
import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional

# Local Imports
try:
    from src.core.encryption.local_crypto import LocalCrypto
    from src.core.storage.walrus_client import WalrusClient
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
    from src.core.encryption.local_crypto import LocalCrypto
    from src.core.storage.walrus_client import WalrusClient

logger = logging.getLogger("LogBundler")
logger.setLevel(logging.INFO)

class FileLogReader:
    """
    Reads .jsonl files tracking the last processed byte offset.
    Persists state to allow resuming after restart.
    """
    def __init__(self, file_path: str, state_file: str):
        self.file_path = file_path
        self.state_file = state_file
        self.last_offset = self._load_state()

    def _load_state(self) -> int:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f).get("offset", 0)
            except:
                return 0
        return 0

    def _save_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"offset": self.last_offset}, f)
        except Exception as e:
            logger.error(f"Failed to save reader state: {e}")

    def read_new_lines(self) -> List[Dict]:
        """Reads new JSON lines from the file since last offset."""
        if not os.path.exists(self.file_path):
            return []

        new_logs = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # Move to last known position
                f.seek(self.last_offset)
                
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.strip():
                        try:
                            new_logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                
                # Update offset
                self.last_offset = f.tell()
                self._save_state()
                
        except Exception as e:
            logger.error(f"Error reading log file {self.file_path}: {e}")
            
        return new_logs

class BatchBundler:
    """
    Periodically bundles, archives, encrypts, and uploads logs.
    """
    def __init__(self, check_interval=150): # 30 mins default
        self.check_interval = check_interval
        self.crypto = LocalCrypto()
        self.storage = WalrusClient()
        self.running = False
        self.worker_thread = None
        
        # Configuration
        self.log_dir = os.path.join(os.getcwd(), "logs")
        self.archives_dir = os.path.join(self.log_dir, "archives")
        self.history_file = os.path.join(self.log_dir, "walrus_history.json")
        os.makedirs(self.archives_dir, exist_ok=True)

        # Readers for alarms and events
        self.readers = {
            "alarms": FileLogReader(
                os.path.join(self.log_dir, "alarms.jsonl"),
                os.path.join(self.log_dir, "alarms_reader_state.json")
            ),
            "events": FileLogReader(
                os.path.join(self.log_dir, "events.jsonl"),
                os.path.join(self.log_dir, "events_reader_state.json")
            )
        }

    def start(self):
        self.running = True
        self.worker_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.worker_thread.start()
        logger.info("📦 BatchBundler Started (30-min Archival Mode)")

    def stop(self):
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()

    # --- Compatibility Methods for SecurityEngine ---
    def ingest_log(self, log_entry: Dict):
        pass # No-op: We read from files now

    def trigger_anomaly(self, anomaly_event: Dict, metadata: Dict):
        pass # No-op: We don't stream anomalies anymore
    # -----------------------------------------------

    def _scheduler_loop(self):
        while self.running:
            try:
                self._process_batch()
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
            
            # Sleep in increments to allow clean stop
            for _ in range(self.check_interval):
                if not self.running: break
                time.sleep(1)

    def _process_batch(self):
        logger.info("⏳ Starting Batch Processing...")
        
        # 1. Read Data
        aggregated_logs = []
        for name, reader in self.readers.items():
            logs = reader.read_new_lines()
            if logs:
                logger.info(f"Read {len(logs)} new records from {name}")
                # Tag source
                for l in logs: l["source"] = name
                aggregated_logs.extend(logs)

        if not aggregated_logs:
            logger.info("No new logs to bundle.")
            return

        # 2. Build Bundle
        timestamp = time.time()
        date_str = datetime.now().strftime("%Y-%m-%d")
        archive_path = os.path.join(self.archives_dir, date_str)
        os.makedirs(archive_path, exist_ok=True)
        
        bundle = {
            "bundle_type": "TRAINING_DATA_BATCH",
            "timestamp": timestamp,
            "record_count": len(aggregated_logs),
            "logs": aggregated_logs
        }
        
        # 3. Archive Locally
        filename = f"bundle_{int(timestamp)}.json"
        local_file_path = os.path.join(archive_path, filename)
        
        with open(local_file_path, "w", encoding='utf-8') as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Local Archive Saved: {local_file_path}")

        # 4. Encrypt
        json_str = json.dumps(bundle, default=str)
        encrypted_payload = self.crypto.encrypt(json_str)
        payload_bytes = json.dumps(encrypted_payload).encode('utf-8')

        # 5. Upload to Walrus
        blob_id = self.storage.store_blob(payload_bytes)
        
        if blob_id:
            logger.info(f"🚀 Uploaded to Walrus! Blob ID: {blob_id}")
            self._update_history(blob_id, timestamp, len(aggregated_logs), local_file_path)
            
            # --- AUTOMATED TRAINING LOOP ---
            try:
                from src.core.ml.trainer import Trainer
                trainer = Trainer()
                # Run in separate thread to not block scheduler
                training_thread = threading.Thread(
                    target=trainer.train_from_walrus,
                    args=(blob_id,),
                    daemon=True
                )
                training_thread.start()
                logger.info("🌪️ Automated Training Triggered!")
            except Exception as e:
                logger.error(f"Failed to trigger training: {e}")
            # -------------------------------
        else:
            logger.error("❌ Walrus Upload Failed")

    def _update_history(self, blob_id, timestamp, count, file_path):
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    history = json.load(f)
            except: pass
            
        record = {
            "id": blob_id,
            "timestamp": timestamp,
            "blob_id": blob_id,
            "file_path": file_path,
            "record_count": count,
            "size_kb": round(os.path.getsize(file_path) / 1024, 2)
        }
        
        history.insert(0, record)
        
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)

# Global Instance
bundler = BatchBundler(check_interval=600) # 10 Minutes
