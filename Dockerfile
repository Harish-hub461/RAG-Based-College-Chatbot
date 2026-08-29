FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and sample docs
COPY backend/ /app/backend/
COPY sample_docs/ /app/sample_docs/

WORKDIR /app/backend

# Hugging Face Spaces exposes port 7860
EXPOSE 7860

# Command to launch FastAPI backend on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
