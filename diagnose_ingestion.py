import os
from src.rag_agent import RAGAgent
from src.utils import ensure_dirs

# Ensure directories exist
ensure_dirs()

# Set mock API key if not present
if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = "MOCK_KEY"

# Create a sample text file
sample_file = "sample.txt"
with open(sample_file, "w") as f:
    f.write("This is a sample document for testing RAG ingestion. It contains some text that will be chunked and indexed.")

try:
    print("Initializing RAGAgent...")
    agent = RAGAgent()

    print(f"Attempting to ingest {sample_file}...")
    # Mocking summarize_document to avoid API call
    original_summarize = agent.summarize_document
    agent.summarize_document = lambda text, filename: "Sample summary"

    result = agent.ingest_document(sample_file, knowledge_area="General")
    print(f"Ingestion result: {result}")

    # Clean up
    if os.path.exists(sample_file):
        os.remove(sample_file)

except Exception as e:
    print(f"Ingestion failed with error: {str(e)}")
    import traceback
    traceback.print_exc()
