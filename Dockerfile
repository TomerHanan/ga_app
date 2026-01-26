# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY test_main.py .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the FastAPI application
CMD ["python", "main.py"]