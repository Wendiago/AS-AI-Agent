import os
from pathlib import Path

class EnvConfig:
    def __init__(self):
        self.OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
        self.SCRAPING_SOURCE_SUBDOMAIN = os.environ.get('SCRAPING_SOURCE_SUBDOMAIN', 'optisigns')
        self.SCRAPING_LIMIT = int(os.environ.get('SCRAPING_LIMIT', 30))
        self.VECTOR_STORE_ID = os.environ.get('VECTOR_STORE_ID', '')
        
        # Base directories from environment
        data_dir = os.environ.get('DATA_DIR', 'data')
        log_dir = os.environ.get('LOG_DIR', 'logs')
        
        # Check if we're in Railway with persistent volume
        persistent_base = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH')
        
        if persistent_base and os.path.exists(persistent_base):
            # Railway
            self.BASE_PATH = Path(persistent_base)
        else:
            # Local: use current directory
            self.BASE_PATH = Path('.')
        
        self.DATA_DIR = self.BASE_PATH / data_dir
        self.LOG_DIR = self.BASE_PATH / log_dir
        self.HASHES_FILE = self.BASE_PATH / 'hashes.json'
        
        # Ensure directories exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOG_DIR.mkdir(exist_ok=True)
            
config = EnvConfig()