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

# Ensure start script is executable
RUN chmod +x start.sh

# Expose port (Back4app will use PORT environment variable)
EXPOSE 8080

# Use start.sh as the entry point
CMD ["./start.sh"]
