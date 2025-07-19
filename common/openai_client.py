import os
from pathlib import Path
from openai import OpenAI
from typing import List, Optional
from openai.types import FilePurpose
from common.env_config import config

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
    
    def list_files(self):
        response = self.client.files.list(purpose="assistants")
        if len(response.data) == 0:
            print("No files found.")
            return
        for file in response.data:
            print(f"{file.filename} [{file.id}]")

    def list_and_delete_file(self):
        while True:
            response = self.client.files.list(purpose="assistants")
            files = list(response.data)
            if len(files) == 0:
                print("No files found.")
                return
            for i, file in enumerate(files, start=1):
                print(f"[{i}] {file.filename} [{file.id}]")
            choice = input("Enter a file number to delete, or any other input to return to menu: ")
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(files):
                return
            selected_file = files[int(choice) - 1]
            self.client.files.delete(selected_file.id)
            print(f"File deleted: {selected_file.filename}")
        
    def delete_all_files(self):
        confirmation = input("This will delete all OpenAI files with purpose 'assistants'.\n Type 'YES' to confirm: ")
        if confirmation == "YES":
            response = self.client.files.list(purpose="assistants")
            for file in response.data:
                self.client.files.delete(file.id)
            print("All files with purpose 'assistants' have been deleted.")
        else:
            print("Operation cancelled.")
            
    def delete_all_files_vector_store(self):
        confirmation = input("This will delete all files with purpose 'assistants' in your vector store.\n Type 'YES' to confirm: ")
        if confirmation == "YES":
            response = self.client.vector_stores.files.list(vector_store_id=config.VECTOR_STORE_ID)
            for file in response.data:
                self.client.vector_stores.files.delete(file.id, vector_store_id=config.VECTOR_STORE_ID)
            print("All files with purpose 'assistants' have been deleted.")
        else:
            print("Operation cancelled.")
       
# Utilities for open ai     
def main():
    while True:
        print("\n== Assistants file utility ==")
        print("[1] List all files")
        print("[2] List all and delete one of your choice")
        print("[3] Delete all assistant files (confirmation required)")
        print("[4] Delete all vector store files (confirmation required)")
        print("[9] Exit")
        choice = input("Enter your choice: ")
        
        openai = OpenAIClient(api_key=config.OPENAI_API_KEY)

        if choice == "1":
            openai.list_files()
        elif choice == "2":
            openai.list_and_delete_file()
        elif choice == "3":
            openai.delete_all_files()
        elif choice == "4":
            openai.delete_all_files_vector_store()
        elif choice == "9":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()