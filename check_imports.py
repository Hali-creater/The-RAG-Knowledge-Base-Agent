try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("langchain_huggingface: OK")
except ImportError:
    print("langchain_huggingface: MISSING")

try:
    from langchain_groq import ChatGroq
    print("langchain_groq: OK")
except ImportError:
    print("langchain_groq: MISSING")

try:
    from langchain_chroma import Chroma
    print("langchain_chroma: OK")
except ImportError:
    print("langchain_chroma: MISSING")
