import os
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader
)
from langchain_core.documents import Document

class DocumentLoader:
    @staticmethod
    def load_document(file_path: str) -> List[Document]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext == '.docx':
            loader = UnstructuredWordDocumentLoader(file_path)
        elif ext == '.txt':
            loader = TextLoader(file_path)
        elif ext == '.md':
            loader = UnstructuredMarkdownLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        return loader.load()

    @staticmethod
    def load_from_directory(directory_path: str) -> List[Document]:
        documents = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                try:
                    documents.extend(DocumentLoader.load_document(file_path))
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        return documents
