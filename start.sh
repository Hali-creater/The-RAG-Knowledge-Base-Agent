#!/bin/bash

# Default port to 8080 if not provided by Back4app
PORT=${PORT:-8080}

# Create necessary directories if they don't exist
mkdir -p data/documents data/chroma_db uploads logs static

if [ "$APP_TYPE" = "streamlit" ]; then
    echo "Starting Streamlit app on port $PORT..."
    streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
else
    echo "Starting FastAPI app on port $PORT..."
    uvicorn main:app --host 0.0.0.0 --port $PORT
fi
