import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class EmbeddingsManager:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._embeddings = None

    def get_embeddings(self):
        if self._embeddings is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found for embeddings. Please set it in your environment or .env file.")
            self._embeddings = OpenAIEmbeddings(
                model=self.model,
                openai_api_key=api_key
            )
        return self._embeddings
