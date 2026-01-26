# Stage 1: Test stage
FROM python:3.11-slim AS test

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and test code
COPY main.py .
COPY test_main.py .

# Run tests
RUN pytest test_main.py -v

# Stage 2: Production stage
FROM python:3.11-slim AS production

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install only production dependencies
RUN pip install -r requirements.txt --no-dev --no-cache-dir

# Copy only application code (not tests)
COPY main.py .
# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]