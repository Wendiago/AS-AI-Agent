from openai import OpenAI
class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()
    
    def upload_document(self, store_name="OptiBotCloneVectorStore"):
        pass