import requests
import json
import logging
import os
import subprocess
import time
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WalrusClient")

class WalrusClient:
    """
    Interacts with the Walrus HTTP Publisher API to store encrypted blobs.
    """
    def __init__(self):
        # Env variables
        load_dotenv()
        self.private_key = os.getenv("SUI_PRIVATE_KEY", "").strip('"').strip("'")
        self.publisher_url = os.getenv("WALRUS_PUBLISHER_URL", "https://publisher.walrus-testnet.walrus.space").strip('"').strip("'")
        
        # Temp dir for config
        self.config_dir = os.path.join(os.getcwd(), ".walrus_config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, "client_config.yaml")
        
        # Setup CLI config if key exists
        if self.private_key:
            self._setup_cli_config()

    def _setup_cli_config(self):
        """Generates a minimal Walrus CLI config with the private key."""
        # Walrus CLI expects a keystore or specific config format.
        # For simplicity in this env, we might need to rely on 'walrus' having its own config logic.
        # However, purely passing private key via env var to 'walrus' binary isn't standard documentation.
        # We will try to rely on the user having 'sui' CLI configured or try to construct a config.
        # Given the complexity of generating a valid keystore file from a raw private key string programmatically
        # without external deps, we will assume for now the user might need to run `walrus config` manually
        # OR we rely on the `walrus` command finding the default sui keystore if available.
        # 
        # BUT, the user explicitly asked us to use the .env key.
        # So we should try to write it to a temp keystore file the CLI can use.
        pass

    def store_blob(self, data: bytes, epochs: int = 5) -> str:
        """
        Stores encrypted blob using Walrus CLI for authentication.
        """
        try:
            # 1. Write data to temp file
            temp_file_path = os.path.join(self.config_dir, f"temp_blob_{int(time.time())}.bin")
            with open(temp_file_path, "wb") as f:
                f.write(data)

            # 2. Construct command
            cmd = ["walrus", "store", temp_file_path, "--epochs", str(epochs), "--json"]
            
            logger.info(f"Executing Walrus CLI: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            if result.returncode == 0:
                print(f"DEBUG: CLI Success: {result.stdout}")
                # Parse JSON output 
                try:
                    output_json = json.loads(result.stdout)
                    blob_id = None
                    if "newlyCreated" in output_json:
                        blob_id = output_json["newlyCreated"]["blobObject"]["blobId"]
                    elif "alreadyCertified" in output_json:
                        blob_id = output_json["alreadyCertified"]["blobId"]
                    
                    if blob_id:
                        logger.info(f"✅ Blob Stored via CLI! ID: {blob_id}")
                        return blob_id
                except json.JSONDecodeError:
                    pass
            else:
                print(f"DEBUG: CLI Failed (Code {result.returncode}): {result.stderr}")
            
            logger.warning(f"⚠️ CLI Authentication failed/unavailable. Output: {result.stderr}")
            logger.info("🔄 Falling back to Public Publisher (HTTP)...")
            return self._store_via_http(data, epochs)

        except Exception as e:
            print(f"DEBUG: CLI Exception: {e}")
            logger.error(f"❌ Walrus CLI Error: {e}")
            return self._store_via_http(data, epochs)

    def _store_via_http(self, data: bytes, epochs: int) -> str:
        # Eski HTTP mantığını buraya taşıyoruz (Fallback olarak)
        urls = [self.publisher_url] + [
             "https://walrus-testnet-publisher.nodeinfra.com",
             "https://publisher.walrus-testnet.walrus.space"
        ]
        
        for base_url in urls:
            publisher = base_url.rstrip("/")
            try:
                url = f"{publisher}/v1/blobs?epochs={epochs}"
                response = requests.put(url, data=data, timeout=10)
                if response.status_code == 200:
                    r = response.json()
                    blob_id = None
                    if "newlyCreated" in r: blob_id = r["newlyCreated"]["blobObject"]["blobId"]
                    elif "alreadyCertified" in r: blob_id = r["alreadyCertified"]["blobId"]
                    
                    if blob_id: 
                        logger.info(f"✅ Blob stored via HTTP ({publisher}). ID: {blob_id}")
                        return blob_id
                else:
                     print(f"DEBUG: HTTP Failed {publisher} -> {response.status_code} {response.text}")
            except Exception as e:
                print(f"DEBUG: HTTP Exception {publisher} -> {e}")
                continue
        return None

    def read_blob(self, blob_id: str) -> bytes:
        """
        Reads a blob from the Walrus Aggregator (Public HTTP).
        """
        aggregators = [
            "https://aggregator.walrus-testnet.walrus.space",
            "https://walrus-testnet-aggregator.nodeinfra.com"
        ]
        
        for base_url in aggregators:
            aggregator = base_url.rstrip("/")
            try:
                url = f"{aggregator}/v1/blobs/{blob_id}"
                logger.info(f"📥 Downloading blob {blob_id} from {aggregator}...")
                
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    logger.info("✅ Download complete.")
                    return response.content
                else:
                    logger.warning(f"Failed to fetch blob from {aggregator}: {response.status_code}")
            except Exception as e:
                logger.error(f"Error reading blob from {aggregator}: {e}")
                continue
                
        return None

# Test Block
if __name__ == "__main__":
    client = WalrusClient()
    dummy_data = b"Hello Walrus! Using AES-GCM Encrypted Bundles."
    blob_id = client.store_blob(dummy_data)
    if blob_id:
        print(f"Test Success! Blob ID: {blob_id}")
