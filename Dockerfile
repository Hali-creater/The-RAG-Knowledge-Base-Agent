FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/documents data/chroma_db uploads logs static

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Default command (can be overridden to run streamlit)
CMD ["python", "main.py"]
