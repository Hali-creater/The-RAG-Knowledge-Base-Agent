import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class EmbeddingsManager:
    def __init__(self, model: str = "text-embedding-3-small"):
        # Check environment or streamlit secrets
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            try:
                import streamlit as st
                api_key = st.secrets.get("OPENAI_API_KEY")
            except Exception:
                pass

        self.embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=api_key
        )

    def get_embeddings(self):
        return self.embeddings
