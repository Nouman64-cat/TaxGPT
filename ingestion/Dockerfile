FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for PyMuPDF or other parsing libraries if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# This copies job.py, extractors.py, indexers.py AND the data/ directory
COPY . .

# Sets the environment variable for the script
ENV DATA_DIR=/app/data

CMD ["python", "job.py"]