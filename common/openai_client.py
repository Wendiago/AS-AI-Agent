import os
from pathlib import Path
from openai import OpenAI
from typing import List, Optional
from openai.types import FilePurpose

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment")
        self.client = OpenAI(api_key=api_key)
        
    def create_vector_store(self, name: str):
        try:
            vector_store = self.client.vector_stores.create(
                name=name,
            )
            print(f"Created vector store: {vector_store.id} ({name})")
            return vector_store.id
        except Exception as e:
            print(f"Error creating vector store: {e}")
            raise
    
    def get_vector_store(self, vector_store_id: str):
        """
        Get vector store details
        """
        try:
            return self.client.vector_stores.retrieve(vector_store_id)
        except Exception as e:
            print(f"Error retrieving vector store {vector_store_id}: {e}")
            raise
        
    def upload_file(self, file_path: Path, purpose: FilePurpose="assistants") -> str:
        try:
            with open(file_path, 'rb') as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose=purpose
                )
            print(f"Uploaded file: {uploaded_file.id} ({file_path.name})")
            return uploaded_file.id
        except Exception as e:
            print(f"Error uploading file {file_path}: {e}")
            raise
        
    def add_file_to_vector_store(self, vector_store_id: str, file_id: str) -> str:
        try:
            vector_store_file = self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            return vector_store_file.id
        except Exception as e:
            print(f"Error adding file {file_id} to vector store {vector_store_id}: {e}")
            raise
    
    def upload_files_to_vector_store(self, vector_store_id: str, file_paths: List[Path]) -> List[str]:
        """
        Upload multiple files to a vector store using batch upload
        """
        try:
            # Upload all files first
            file_ids = []
            for file_path in file_paths:
                file_id = self.upload_file(file_path)
                file_ids.append(file_id)
            
            # Create batch upload to vector store
            batch = self.client.vector_stores.file_batches.create(
                vector_store_id=vector_store_id,
                file_ids=file_ids
            )
            
            print(f"Created batch upload: {batch.id} with {len(file_ids)} files")
            return file_ids
        except Exception as e:
            print(f"Error batch uploading files to vector store {vector_store_id}: {e}")
            raise
        
    def get_file_chunks(self, vector_store_id: str, file_id: str):
        """
        Get chunks for a specific file in a vector store
        """
        try:
            return self.client.vector_stores.files.retrieve(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
        except Exception as e:
            print(f"Error getting chunks for file {file_id} in vector store {vector_store_id}: {e}")
            raise
        
    def get_vector_store_files(self, vector_store_id: str, limit: int = 100):
        """
        Get files in a vector store
        """
        try:
            return self.client.vector_stores.files.list(
                vector_store_id=vector_store_id,
                limit=limit
            )
        except Exception as e:
            print(f"Error getting files from vector store {vector_store_id}: {e}")
            raise