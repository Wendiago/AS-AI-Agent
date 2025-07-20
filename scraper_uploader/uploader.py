import os
import json
from datetime import timezone, datetime
from pathlib import Path
from typing import List, Optional, cast
from common.openai_client import OpenAIClient
from common.env_config import config

class Uploader:
    def __init__(self, vector_store_id: Optional[str] = None, vector_store_name: Optional[str] = None):
        """
        Initialize the Uploader with OpenAI client and vector store configuration
        
        Args:
            vector_store_id: Existing vector store ID to use
            vector_store_name: Name for new vector store if vector_store_id is not provided
        """
        self.data_dir = config.DATA_DIR
        self.upload_log_dir = config.LOG_DIR / "upload"
        
        # Initialize OpenAI client
        self.openai_client = OpenAIClient(api_key=config.OPENAI_API_KEY)
        
        # Set up vector store
        self.vector_store_id = vector_store_id
        if not self.vector_store_id:
            if not vector_store_name:
                vector_store_name = f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.vector_store_id = self.openai_client.create_vector_store(
                name=vector_store_name,
            )
        
        print(f"Using vector store: {self.vector_store_id}")
        
        # Ensure directories exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.upload_log_dir).mkdir(parents=True, exist_ok=True)
        
    def upload_files_to_vector_store(self, files: List[Path]) -> List[str]:
        """
        Upload files to the vector store
        
        Args:
            files: List of file paths to upload
            
        Returns:
            List of file IDs that were uploaded
        """
        if not files:
            return []
        
        print(f"Uploading {len(files)} files to vector store...")
        
        # Upload files using batch upload
        file_ids = self.openai_client.upload_files_to_vector_store(
            cast(str, self.vector_store_id), #Avoid pylance alert
            files
        )
        
        for file_path in files:
            print(f"Uploaded: {file_path.name}")
        
        return file_ids
        
    def write_upload_log(self, uploaded_count: int):
        """
        Write upload log with statistics
        """
        utc_now = datetime.now(timezone.utc)
        log_filename = f"{utc_now.date()}.json"
        log_file = os.path.join(self.upload_log_dir, log_filename)
        
        # Load existing logs if file exists
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        
        # Append this run
        logs.append({
            "timestamp": utc_now.isoformat(),
            "vector_store_id": self.vector_store_id,
            "embedded_files": uploaded_count,
        })
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
        
        print(f"Upload complete: {uploaded_count} files uploaded.")
        print(f"Log written to {log_filename}")