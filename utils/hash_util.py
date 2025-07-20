import json, hashlib, os
from common.env_config import config

class HashUtil:
    @staticmethod
    def load_hashes():
        """
        Load articles hash if exists
        """
        if os.path.exists(config.HASHES_FILE):
            with open(config.HASHES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_hashes(hashes):
        with open(config.HASHES_FILE, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2)
        
    @staticmethod
    def calculate_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()