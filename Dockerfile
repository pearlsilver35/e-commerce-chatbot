FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    sqlite3 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/chroma_db

# Preload the ChromaDB embedding model to avoid first-request delay
# Create directory and fully download the model before running the app
RUN mkdir -p /root/.cache/chroma/onnx_models
# Force full download of model and prevent runtime downloads
RUN python -c "from chromadb.utils import embedding_functions; ef = embedding_functions.DefaultEmbeddingFunction(); ef(['This is a test to ensure model is fully downloaded'])"
# Verify the model files are properly downloaded
RUN ls -la /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=8501"] 